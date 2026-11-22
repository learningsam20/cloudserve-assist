"""FastAPI entrypoint for CloudServe Assistant."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, Field

from src import __version__
from src.config import get_settings
from src.graph import run_ticket
from src.models import PipelineResult
from src.observability import metrics_payload

app = FastAPI(title="CloudServe Assistant", version=__version__)


class TicketRequest(BaseModel):
    ticket: dict[str, Any] = Field(..., description="Raw ticket object (Capstone schema)")
    allow_generate: bool = True


@app.get("/health")
def health() -> dict[str, Any]:
    settings = get_settings()
    chroma: dict[str, Any] = {"ok": False}
    try:
        from src.retrieve import index_stats

        chroma = {"ok": True, **index_stats()}
    except Exception as exc:  # noqa: BLE001
        chroma = {"ok": False, "error": str(exc)}
    return {
        "status": "ok",
        "service": "CloudServe Assistant",
        "version": __version__,
        "kill_switch": settings.kill_switch_active(),
        "chroma": chroma,
    }


@app.get("/metrics")
def metrics() -> Response:
    payload, content_type = metrics_payload()
    return Response(content=payload, media_type=content_type)


@app.post("/tickets/process", response_model=PipelineResult)
def process_ticket(body: TicketRequest) -> PipelineResult:
    if not body.ticket:
        raise HTTPException(status_code=400, detail="ticket object required")
    return run_ticket(body.ticket, persist=True, allow_generate=body.allow_generate)


def main() -> None:
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.api:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,
    )


if __name__ == "__main__":
    main()
