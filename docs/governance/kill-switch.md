# Kill switch — CloudServe Assistant

Semantics locked in `docs/plan/findings.md` § D4.

## How to activate

1. Set `KILL_SWITCH=true` in `.env`, **or**
2. Create the file at `KILL_SWITCH_FILE` (default `./storage/KILL_SWITCH`).

## Behaviour

| Scope | Effect |
|-------|--------|
| Route (every ticket) | Force `escalate`; never `auto_respond` |
| In-flight generate | Call may finish; result is not treated as auto-send (route already blocked new autos) |
| Harness / API queue | Continues; remaining tickets escalate |
| `/health` | Exposes `kill_switch: true` |

Takes effect on the **next route decision** — no redeploy required.

## Verify

```bash
touch storage/KILL_SWITCH
curl -s localhost:8000/health   # kill_switch true
```
