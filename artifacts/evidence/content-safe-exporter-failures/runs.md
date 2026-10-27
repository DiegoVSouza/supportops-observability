# Phase 014 run record

Model and exporter tests use fakes/in-memory spans only. No credentials, provider, OTLP endpoint, external network, or live telemetry service was accessed. Full gate used `P03_SKIP_SERVICES=1`; it did not start service stacks. The already-cached local Prometheus validator ran as a transient `--rm` container.

| Command | Exit | Output |
|---|---:|---|
| `uv run --locked --extra dev pytest tests/test_instrumentation.py tests/test_live_groq_eval.py -q` | 0 | `focused-tests.txt` |
| `uv run --locked --extra dev python scripts/check_full.py` | 2 | `full-gate.txt` |
| `uv run --locked --extra dev pytest tests/test_instrumentation.py -q` (red before implementation) | 1 expected | `red-tests.txt`; failures exposed absent safe error categories and lifecycle status. |

The full gate ran 50 tests with zero failures. Prometheus rules, Compose config, and lock validation passed; the required service integration gate was intentionally skipped and status is INCOMPLETE (exit 2). Detailed output: `generated-check-full.txt`. All pre-existing artifact files outside this phase directory were byte-identical after checks. Docker project snapshots are recorded before/after; one volatile unrelated container status transition occurred in read-only inventory polling, while project summaries and P03 identities remained stable.
