# Demonstration video — CloudServe Assistant

**Status: NOT YET RECORDED.**  
**Target length: ≤18 minutes** (with **≥7 minutes** live demo + evaluation walkthrough).  
**Script:** [video-script.md](video-script.md) — each beat is **[SHOW]** + **[SAY]**; tickets **VAL-0010** / **VAL-0002** in `storage/demo_tickets/`.

`scripts/package_submission.sh` copies this folder’s README, script, and any `.mp4` / `.mov` / `.webm` / `.m4v` into package `01_Video/`.

## Before you record

1. Build and evaluation artefacts are already on disk. Day-of work is demo fixtures, a dry-run, and the recording.  
2. Follow the prep and live-demo sections in [video-script.md](video-script.md).  
3. For generate-on FCR, point at the existing run `evaluation/results/validation_20261122T131433Z/` (LiteLLM → Groq, FCR 82.5%). Optional: one live generate on `ticket_auto_generate.json`.  
4. Never show `.env` or API keys.  
5. Record take 1, then take 2 (Submission Guide advice).

## After you record

1. Name file `FirstnameLastname_CloudServe_Demo.mp4` (1080p).  
2. Put it in this folder.  
3. Change status above to **RECORDED**.  
4. Continue root `instructions.md` packaging steps.
