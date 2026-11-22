"""LangGraph StateGraph orchestration — API and harness share run_ticket."""

from __future__ import annotations

import time
from typing import Any, Optional, TypedDict

from langgraph.graph import END, StateGraph

from src.classify import classify
from src.config import get_settings
from src.generate import generate
from src.guardrails import final_action, validate
from src.ingest import ingest
from src.logging_store import log_decision, log_pipeline_result
from src.models import (
    Classification,
    GenerationResult,
    GuardrailResult,
    Passage,
    PipelineResult,
    RouteAction,
    RouteDecision,
    Ticket,
    Urgency,
)
from src.observability import observe_errors, observe_result
from src.retrieve import retrieve
from src.route import route


class TicketState(TypedDict, total=False):
    raw: Any
    ticket: Optional[Ticket]
    classification: Optional[Classification]
    passages: list[Passage]
    decision: Optional[RouteDecision]
    generation: Optional[GenerationResult]
    guardrails: list[GuardrailResult]
    action: RouteAction
    errors: list[str]
    allow_generate: bool
    persist: bool
    escalation_summary: Optional[str]
    ingest_failed: bool


def _escalation_package(
    ticket: Ticket,
    classification: Optional[Classification],
    passages: list[Passage],
    decision: Optional[RouteDecision],
) -> str:
    intent = classification.intent if classification else "unknown"
    urgency = classification.urgency.value if classification else "unknown"
    conf = classification.confidence if classification else 0.0
    sources = ", ".join(f"{p.doc_id}({p.score:.2f})" for p in passages[:5]) or "(none)"
    reason = decision.reason if decision else "n/a"
    return (
        f"ESCALATION for {ticket.ticket_id}\n"
        f"channel={ticket.channel.value} intent={intent} urgency={urgency} "
        f"confidence={conf:.3f}\n"
        f"route_reason={reason}\n"
        f"sources={sources}\n"
        f"subject={ticket.subject[:200]}"
    )


def node_ingest(state: TicketState) -> TicketState:
    errors = list(state.get("errors") or [])
    raw = state.get("raw")
    try:
        if isinstance(raw, Ticket):
            ticket = raw
        else:
            ticket = ingest(raw if isinstance(raw, dict) else {})
        return {
            **state,
            "ticket": ticket,
            "errors": errors,
            "ingest_failed": False,
            "passages": [],
            "guardrails": [],
        }
    except Exception as exc:  # noqa: BLE001
        tid = "unknown"
        if isinstance(raw, dict):
            tid = str(raw.get("ticket_id") or "unknown")
        elif isinstance(raw, Ticket):
            tid = raw.ticket_id
        errors.append(f"ingest_failed: {exc}")
        # Minimal ticket so logging / escalate path can proceed (A8)
        from src.models import Channel

        ticket = Ticket(ticket_id=tid, channel=Channel.EMAIL, subject="", body="")
        return {
            **state,
            "ticket": ticket,
            "errors": errors,
            "ingest_failed": True,
            "action": RouteAction.ESCALATE,
            "passages": [],
            "guardrails": [],
            "decision": RouteDecision(
                action=RouteAction.ESCALATE,
                reason=f"Ingest failed: {exc}",
                threshold_applied=0.0,
            ),
        }


def node_classify(state: TicketState) -> TicketState:
    if state.get("ingest_failed"):
        return {
            **state,
            "classification": Classification(
                intent="unclear_request",
                urgency=Urgency.MEDIUM,
                confidence=0.0,
                source="fallback",
            ),
        }
    errors = list(state.get("errors") or [])
    ticket = state["ticket"]
    assert ticket is not None
    try:
        classification = classify(ticket)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"classify_failed: {exc}")
        classification = Classification(
            intent="unclear_request",
            urgency=Urgency.MEDIUM,
            confidence=0.0,
            source="fallback",
        )
    return {**state, "classification": classification, "errors": errors}


def node_retrieve(state: TicketState) -> TicketState:
    if state.get("ingest_failed"):
        return {**state, "passages": []}
    errors = list(state.get("errors") or [])
    ticket = state["ticket"]
    assert ticket is not None
    try:
        passages = retrieve(ticket)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"retrieve_failed: {exc}")
        passages = []
    return {**state, "passages": passages, "errors": errors}


def node_route(state: TicketState) -> TicketState:
    if state.get("ingest_failed") and state.get("decision") is not None:
        return state
    errors = list(state.get("errors") or [])
    ticket = state["ticket"]
    classification = state.get("classification")
    passages = list(state.get("passages") or [])
    assert ticket is not None
    if classification is None:
        classification = Classification(
            intent="unclear_request",
            urgency=Urgency.MEDIUM,
            confidence=0.0,
            source="fallback",
        )
    try:
        decision = route(ticket, classification, passages)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"route_failed: {exc}")
        decision = RouteDecision(
            action=RouteAction.ESCALATE,
            reason=f"Routing error: {exc}",
            threshold_applied=0.0,
        )
    action = decision.action
    out: TicketState = {
        **state,
        "classification": classification,
        "decision": decision,
        "action": action,
        "errors": errors,
    }
    if action == RouteAction.ESCALATE:
        out["escalation_summary"] = _escalation_package(
            ticket, classification, passages, decision
        )
    return out


def node_generate(state: TicketState) -> TicketState:
    allow = bool(state.get("allow_generate", True))
    action = state.get("action") or RouteAction.ESCALATE
    if not allow or action != RouteAction.AUTO_RESPOND:
        return state

    # Mid-flight kill re-check (findings D4) before spending tokens / shipping.
    settings = get_settings()
    if settings.kill_switch_active():
        decision = RouteDecision(
            action=RouteAction.ESCALATE,
            reason="Kill switch active mid-flight; auto_respond aborted (findings D4).",
            threshold_applied=settings.confidence_threshold,
            kill_switch=True,
            grounded_override=False,
        )
        ticket = state["ticket"]
        assert ticket is not None
        return {
            **state,
            "decision": decision,
            "action": RouteAction.ESCALATE,
            "generation": None,
            "escalation_summary": _escalation_package(
                ticket, state.get("classification"), list(state.get("passages") or []), decision
            ),
        }

    errors = list(state.get("errors") or [])
    ticket = state["ticket"]
    passages = list(state.get("passages") or [])
    classification = state.get("classification")
    decision = state.get("decision")
    assert ticket is not None
    try:
        generation = generate(ticket, passages)
        skip_floor = bool(decision and decision.grounded_override)
        guardrail_results, blocked = validate(
            generation,
            passages,
            classification=classification,
            confidence_threshold=settings.confidence_threshold,
            skip_confidence_floor=skip_floor,
        )
        action = final_action(action, blocked=blocked)
        if blocked and decision is not None:
            decision = RouteDecision(
                action=RouteAction.BLOCK,
                reason="Blocked by guardrails: "
                + "; ".join(g.detail for g in guardrail_results if not g.passed),
                threshold_applied=decision.threshold_applied,
                kill_switch=decision.kill_switch,
                grounded_override=decision.grounded_override,
            )
            action = RouteAction.BLOCK

        # Mid-flight kill re-check after generate (race with ops flip).
        if settings.kill_switch_active() and action == RouteAction.AUTO_RESPOND:
            decision = RouteDecision(
                action=RouteAction.ESCALATE,
                reason="Kill switch activated after generate; suppressing auto_respond (D4).",
                threshold_applied=settings.confidence_threshold,
                kill_switch=True,
                grounded_override=False,
            )
            action = RouteAction.ESCALATE
            generation = None

        out: TicketState = {
            **state,
            "generation": generation,
            "guardrails": guardrail_results,
            "decision": decision,
            "action": action,
            "errors": errors,
        }
        if action == RouteAction.ESCALATE:
            out["escalation_summary"] = _escalation_package(
                ticket, classification, passages, decision
            )
        return out
    except Exception as exc:  # noqa: BLE001 — provider failure → escalate (A11)
        errors.append(f"generate_or_validate_failed: {exc}")
        decision = RouteDecision(
            action=RouteAction.ESCALATE,
            reason=f"Generation/validation failed: {exc}",
            threshold_applied=(
                decision.threshold_applied if decision is not None else settings.confidence_threshold
            ),
            kill_switch=decision.kill_switch if decision is not None else False,
            grounded_override=False,
        )
        return {
            **state,
            "generation": None,
            "decision": decision,
            "action": RouteAction.ESCALATE,
            "errors": errors,
            "escalation_summary": _escalation_package(
                ticket, classification, passages, decision
            ),
        }


def node_persist(state: TicketState) -> TicketState:
    ticket = state.get("ticket")
    action = state.get("action") or RouteAction.ESCALATE
    errors = list(state.get("errors") or [])
    result = PipelineResult(
        ticket_id=ticket.ticket_id if ticket else "unknown",
        classification=state.get("classification"),
        passages=list(state.get("passages") or []),
        route=state.get("decision"),
        generation=state.get("generation"),
        guardrails=list(state.get("guardrails") or []),
        action=action,
        errors=errors,
        escalation_summary=state.get("escalation_summary"),
    )
    if state.get("persist", True):
        try:
            if ticket is not None:
                log_pipeline_result(result, ticket_text_summary=ticket.text_for_model()[:500])
            else:
                log_decision(
                    ticket_id=result.ticket_id,
                    stage="routing",
                    action_taken=action.value,
                    reason="persist without ticket object",
                    requirement_ids=["A8"],
                )
        except Exception as exc:  # noqa: BLE001
            errors.append(f"decision_log_failed: {exc}")
            result.errors = errors
    return {**state, "errors": errors, "action": result.action}


def _build_graph():
    g = StateGraph(TicketState)
    g.add_node("ingest", node_ingest)
    g.add_node("classify", node_classify)
    g.add_node("retrieve", node_retrieve)
    g.add_node("route", node_route)
    g.add_node("generate", node_generate)
    g.add_node("persist", node_persist)
    g.set_entry_point("ingest")
    g.add_edge("ingest", "classify")
    g.add_edge("classify", "retrieve")
    g.add_edge("retrieve", "route")
    g.add_edge("route", "generate")
    g.add_edge("generate", "persist")
    g.add_edge("persist", END)
    return g.compile()


_COMPILED = None


def get_compiled_graph():
    global _COMPILED
    if _COMPILED is None:
        _COMPILED = _build_graph()
    return _COMPILED


def run_ticket(
    raw_or_ticket: dict[str, Any] | Ticket,
    *,
    persist: bool = True,
    allow_generate: bool = True,
) -> PipelineResult:
    """Ingest → classify → retrieve → route → (generate) → validate → log via LangGraph."""
    t0 = time.perf_counter()
    graph = get_compiled_graph()
    final: TicketState = graph.invoke(
        {
            "raw": raw_or_ticket,
            "allow_generate": allow_generate,
            "persist": persist,
            "errors": [],
            "passages": [],
            "guardrails": [],
            "action": RouteAction.ESCALATE,
        }
    )
    ticket = final.get("ticket")
    action = final.get("action") or RouteAction.ESCALATE
    result = PipelineResult(
        ticket_id=ticket.ticket_id if ticket else "unknown",
        classification=final.get("classification"),
        passages=list(final.get("passages") or []),
        route=final.get("decision"),
        generation=final.get("generation"),
        guardrails=list(final.get("guardrails") or []),
        action=action,
        errors=list(final.get("errors") or []),
        escalation_summary=final.get("escalation_summary"),
    )
    blocked = [g.name for g in result.guardrails if not g.passed]
    observe_result(result.action.value, time.perf_counter() - t0, blocked_guards=blocked)
    observe_errors(len(result.errors))
    return result
