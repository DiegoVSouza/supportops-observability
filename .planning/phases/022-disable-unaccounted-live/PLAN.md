# Plan

1. Make the legacy entry refuse before credential, provider and evidence access; add an offline regression.
2. Run locked focused and local fake checks and record sanitized command, cwd, exit and output.

allowed_write_paths: `.planning/phases/022-disable-unaccounted-live/**`, `scripts/run_live_groq_eval.py`, `tests/test_live_groq_eval.py`, `artifacts/evidence/disable-unaccounted-live-022/**`.

forbidden_changes: historical evidence, unrelated artifacts, other projects, budgets, credentials, live calls, existing test assertions, Docker lifecycle, paid use, external effects or human review. Budget zero calls, USD 0. max_tries: 3 per failure; never replay live work. Stop on unexpected external access. Plan-check is implementer self-assessment.
