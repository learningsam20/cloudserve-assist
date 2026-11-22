# Incident procedure — CloudServe Assistant

Short runbook for unsafe auto-replies, provider outages, or suspected data leakage.

## 1. Contain (minutes)

1. Activate kill switch: `KILL_SWITCH=true` or `touch storage/KILL_SWITCH`.
2. Confirm `/health` shows `"kill_switch": true`.
3. Stop further deploys that would clear the kill file.

All new tickets escalate; no `auto_respond`.

## 2. Triage

1. Export decisions: harness output `decisions_export.jsonl` or SQLite `storage/decisions.db`.
2. Filter recent `action_taken` / guardrail failures for the incident window.
3. Note model id, prompt version (`PR-GEN-01-v1.0`), and `threshold_applied`.

## 3. Eradicate / recover

| Incident | Action |
|----------|--------|
| Bad generation / hallucination | Keep kill on; patch prompt or guards; re-test with `--no-generate` then limited generate |
| Provider outage | Escalate-only is safe; restore when OpenRouter healthy; cache reduces repeat cost |
| PII in outbound | Kill on; extend PII patterns; sample audit of generated answers in results.jsonl |
| Threshold regression | Revert `CONFIDENCE_THRESHOLD` to frozen 0.35 unless a logged PRD revision says otherwise |

## 4. Close

1. Clear kill only after a written go-ahead.
2. Append a one-line note to `docs/plan/work-log.md` (date, symptom, action).
3. If customer-facing text may have leaked, follow CloudServe’s human support escalation path (out of band).
