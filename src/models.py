"""Shared domain models for CloudServe Assistant."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class Channel(str, Enum):
    EMAIL = "email"
    CHAT = "chat"
    DOCS_COMMENT = "docs_comment"
    FORUM = "forum"


class Urgency(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RouteAction(str, Enum):
    AUTO_RESPOND = "auto_respond"
    ESCALATE = "escalate"
    BLOCK = "block"


class Ticket(BaseModel):
    ticket_id: str
    channel: Channel
    subject: str = ""
    body: str = ""
    received_at: Optional[str] = None
    customer_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_tier: Optional[str] = None
    customer_region: Optional[str] = None
    language_fluency: Optional[str] = None
    # Optional eval-only fields when present in JSON
    labels: Optional[dict[str, Any]] = None
    history: Optional[dict[str, Any]] = None

    def text_for_model(self) -> str:
        return f"{self.subject}\n{self.body}".strip()


class Alternative(BaseModel):
    value: str
    confidence: float


class Classification(BaseModel):
    intent: str
    urgency: Urgency
    confidence: float = Field(ge=0.0, le=1.0)
    alternatives: list[Alternative] = Field(default_factory=list)
    source: Literal["rules", "model", "fallback"] = "model"
    rule_id: Optional[str] = None


class Passage(BaseModel):
    doc_id: str
    text: str
    score: float
    title: Optional[str] = None


class RouteDecision(BaseModel):
    action: RouteAction
    reason: str
    threshold_applied: float
    kill_switch: bool = False
    grounded_override: bool = False


class GenerationResult(BaseModel):
    answer: str
    citation_doc_ids: list[str] = Field(default_factory=list)
    model: Optional[str] = None
    cached: bool = False


class GuardrailResult(BaseModel):
    name: str
    passed: bool
    detail: str = ""


class PipelineResult(BaseModel):
    ticket_id: str
    classification: Optional[Classification] = None
    passages: list[Passage] = Field(default_factory=list)
    route: Optional[RouteDecision] = None
    generation: Optional[GenerationResult] = None
    guardrails: list[GuardrailResult] = Field(default_factory=list)
    action: RouteAction = RouteAction.ESCALATE
    errors: list[str] = Field(default_factory=list)
    # Tier-2 package when escalating (Build Spec Route section)
    escalation_summary: Optional[str] = None
