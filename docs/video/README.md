# Demonstration video — CloudServe Assistant

**Status: RECORDED** (revision may replace the file before hand-in).  
**Working file:** [demo.mp4](demo.mp4)  
**Packaged name (Submission Guide):** `SameerJ_Capstone_Video.mp4`

`scripts/package_submission.sh` copies this README and renames the recording to  
`{STUDENT_SLUG}_Capstone_Video.mp4` (default `SameerJ`) inside package `01_Video/`.

## After revising the video

1. Replace `docs/video/demo.mp4` with the new recording (1080p or better).  
2. Re-run:

```bash
PACKAGE_OUT=../_package STUDENT_SLUG=SameerJ ./scripts/package_submission.sh
```

3. Confirm `_package/SameerJ_Capstone_Submission/01_Video/SameerJ_Capstone_Video.mp4`.

## Contents of the recording

- Product problem and findings D1–D5 (threshold freeze at 0.35)
- Architecture / data-flow diagrams
- Live API: health, auto_respond, policy escalate, guardrail block, kill switch, short harness
- Evaluation: route-only and generate-on evidence (FCR 82.5%, LiteLLM → Groq)
