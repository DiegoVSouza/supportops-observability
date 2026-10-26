# P03 verification

- Confirm P03-local path ownership and that no prompts/content are captured.
- Run offline mocked live-client tests, instrumentation tests, and `scripts/check_full.py`; record commands/exits/output.
- Confirm model availability via authenticated Groq catalog before one completion.
- Ensure the response is passed through `record_llm_call` in an active agent span. Verify trace has an LLM inference span, expected model/provider/usage attributes, and no content attribute; inspect Prometheus metrics for one real observation.
- Save sanitized metadata, usage, latency, attempt count, status, and command/exit evidence in `artifacts/evidence/phase-010-groq-live.*`.
- Leave cost `PENDING` absent billing evidence; no provider fallback. Commit locally, no push.

## Recorded result — 2026-10-26

- Focused instrumentation suite passed (31 tests). Full check reports `INCOMPLETE` only because `promtool` and Docker services are unavailable; deterministic tests/demo/compose config passed.
- Live command: `LLM_MODE=live uv run --extra live --extra dev python scripts/run_live_groq_eval.py`; exit 0. Four-key model preflight passed; 103 input / 82 output tokens; latency 0.420243 s; model/provider/usage span assertions passed; no content attribute; estimated cost USD 0.000032325, billed cost `PENDING`.
- One actual LLM span and metrics were recorded. Only actual-run measurements are in this phase artifact; fake telemetry remains test-only.
