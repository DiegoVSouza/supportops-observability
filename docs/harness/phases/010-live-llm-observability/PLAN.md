# P03 execution plan

## Task 1 — Add offline telemetry contract tests

Use mocked SDK responses and an in-memory span exporter to verify usage/model/provider attributes, success/error outcomes, metrics, and that response content is not captured by default.

## Task 2 — Implement a bounded Groq telemetry run

Add an optional Groq SDK dependency and a P03 script that makes one synthetic completion, records the real `LLMResponse` with existing P03 instrumentation, and writes sanitized trace/usage evidence. Do not alter telemetry package public contracts.

## Task 3 — Validate and run

Run P03 focused and full offline checks, then perform one authenticated model-list preflight and one real call under free-plan limits. Review privacy, metrics, cost status, and staged diff.

## Ownership

`allowed_write_paths`: `docs/harness/phases/010-live-llm-observability/**`, `scripts/run_live_groq_eval.py`, `tests/test_live_groq_eval.py`, `pyproject.toml`, `uv.lock`, `harness.yaml` (enable the now-present capability eval), `README.md`, `docs/harness/decisions.md`, `docs/harness/progress.md`, `artifacts/evidence/phase-010-groq-*`.

`forbidden_changes`: `harness-kit/**`, `.env`, other projects, existing synthetic trace fixtures, service stack, or unrelated metrics.

## Runtime limits

- Explicit `LLM_MODE=live`; Groq `openai/gpt-oss-20b`; one preflight and one response; <=128 completion tokens and 20s timeout.
- At most one bounded pass over configured unique keys for retryable throttling/transient failures. No auth/model/validation retries or provider fallback.
- Existing configured paid budget is USD 0; use only the user-designated free tier. Actual billed cost remains `PENDING` if not verifiable.

## Validation

Run focused telemetry tests and P03's documented full check. Store commands, exit codes, sanitized output, and phase status in evidence.
