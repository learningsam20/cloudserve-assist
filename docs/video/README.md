# Demonstration video — CloudServe Assistant

**Status: NOT YET RECORDED.**  
**Target length: ≤18 minutes** (with **≥7 minutes** live demo + **eval walkthrough**).  
**Script:** `video-script.md` — each beat is **[SHOW]** + **[SAY]**; tickets **VAL-0010** / **VAL-0002** in `storage/demo_tickets/`.

`scripts/package_submission.sh` copies this folder’s README, script, and any `.mp4` / `.mov` / `.webm` / `.m4v` into package `01_Video/`.

## Before you record

1. Most build/eval work is **already done** (see “Already done” in `video-script.md`). You mainly need demo ticket JSON, a day-of dry-run, and the recording.  
2. Follow **§A2–B** in `video-script.md` (write `storage/demo_tickets/*.json`, dry-run).  
3. Choose Plan A (live generate) or Plan B (route-only + guardrail pytest) and say it on camera. Point at **existing** `validation_20261122T131433Z` for FCR — do not re-run full generate-on on camera unless you want to.  
4. Never show `.env` or API keys.  
5. Record take 1, then take 2 (Submission Guide advice).

## After you record

1. Name file `FirstnameLastname_CloudServe_Demo.mp4` (1080p).  
2. Put it in this folder.  
3. Change status above to **RECORDED**.  
4. Continue root `instructions.md` packaging steps.
