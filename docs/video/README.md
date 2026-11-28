# Demonstration video — CloudServe Assistant

**Status: RECORDED.**  
**Recording:** [demo.mp4](demo.mp4) (~21 min; live API walkthrough + evaluation).

`scripts/package_submission.sh` copies this README and any `.mp4` / `.mov` / `.webm` / `.m4v` in this folder into package `01_Video/`. For the release zip, rename the file to `FirstnameLastname_CloudServe_Demo.mp4` if the Submission Guide requires that exact name.

## Contents of the recording

- Product problem and findings D1–D5 (threshold freeze at 0.35)
- Architecture / data-flow diagrams
- Live API: health, VAL-0010 auto_respond, VAL-0002 policy escalate, guardrail block, kill switch, short harness
- Evaluation: route-only `validation_fairness_fix` and generate-on `validation_20261122T131433Z` (FCR 82.5%, LiteLLM → Groq)

## Package

1. Confirm [demo.mp4](demo.mp4) is in this folder.  
2. Run `PACKAGE_NO_ZIP=1 ./scripts/package_submission.sh` (or omit `PACKAGE_NO_ZIP` to zip).  
3. Ensure `01_Video/` contains the recording; rename to the enrolment demo filename if required.
