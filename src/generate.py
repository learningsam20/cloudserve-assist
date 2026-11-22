"""Grounded generation via LiteLLM → OpenRouter, with disk cache."""

from __future__ import annotations

import json
import re
from typing import Any

from src.cache import get_cached, put_cached
from src.config import get_settings
from src.llm import completion
from src.models import GenerationResult, Passage, Ticket


def _load_prompt_body() -> str:
    return get_settings().prompt_file.read_text(encoding="utf-8")


def _passages_block(passages: list[Passage]) -> str:
    parts = []
    for i, p in enumerate(passages, start=1):
        title = p.title or ""
        parts.append(f"[{i}] doc_id={p.doc_id} title={title}\n{p.text}")
    return "\n\n".join(parts)


def _extract_system_and_json_contract(prompt_doc: str) -> tuple[str, str]:
    """Pull ## System body and any trailing JSON-only contract from the prompt file."""
    system = prompt_doc
    json_contract = (
        'Respond with JSON only:\n'
        '{\n'
        '  "answer": "<customer-facing draft>",\n'
        '  "citation_doc_ids": ["DOC-..."],\n'
        '  "automated_disclosure": true\n'
        '}'
    )
    if "## System" in prompt_doc:
        after = prompt_doc.split("## System", 1)[1]
        if "##" in after:
            system = after.split("##", 1)[0].strip()
        else:
            system = after.strip()
    # Prefer explicit contract text living after the User template in the file.
    if "Respond with JSON only" in prompt_doc:
        json_contract = prompt_doc.split("Respond with JSON only", 1)[1]
        json_contract = "Respond with JSON only" + json_contract
        # Stop before any later markdown heading if present
        if "\n## " in json_contract:
            json_contract = json_contract.split("\n## ", 1)[0]
        json_contract = json_contract.strip()
    system = f"{system}\n\n{json_contract}".strip()
    return system, json_contract


def _build_messages(ticket: Ticket, passages: list[Passage]) -> list[dict[str, str]]:
    # Versioned prompt file is the source of truth.
    prompt_doc = _load_prompt_body()
    system, json_contract = _extract_system_and_json_contract(prompt_doc)
    user = (
        f"TICKET_BEGIN\n{ticket.text_for_model()}\nTICKET_END\n\n"
        f"PASSAGES_BEGIN\n{_passages_block(passages)}\nPASSAGES_END\n\n"
        f"{json_contract}"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]


def _parse_json_content(content: str) -> dict[str, Any]:
    content = content.strip()
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def generate(ticket: Ticket, passages: list[Passage]) -> GenerationResult:
    """Draft a cited answer. Requires passages; caller must not invoke on empty retrieve."""
    settings = get_settings()
    if not passages:
        return GenerationResult(
            answer="I do not have enough documentation to answer safely. Escalating to a human agent.",
            citation_doc_ids=[],
            model=None,
            cached=False,
        )

    messages = _build_messages(ticket, passages)
    prompt_key = json.dumps(messages, ensure_ascii=False, sort_keys=True)
    model = settings.litellm_model

    cached = get_cached(model, prompt_key)
    if cached is not None:
        return GenerationResult(
            answer=str(cached.get("answer") or ""),
            citation_doc_ids=[str(x) for x in cached.get("citation_doc_ids") or []],
            model=model,
            cached=True,
        )

    raw = completion(messages, temperature=settings.llm_temperature)
    data = _parse_json_content(raw)
    answer = str(data.get("answer") or "").strip()
    citations = [str(x) for x in (data.get("citation_doc_ids") or [])]
    payload = {
        "answer": answer,
        "citation_doc_ids": citations,
        "prompt_version": settings.prompt_version,
    }
    put_cached(model, prompt_key, payload)
    return GenerationResult(answer=answer, citation_doc_ids=citations, model=model, cached=False)
