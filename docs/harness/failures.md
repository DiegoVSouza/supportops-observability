# Failures

Record recurring builder or product failures here before fixing them.

## 2026-10-26 — Live acceptance finding

The first Docker gate exceeded its cold-start synthetic-alert wait. All four alerts later fired; increasing the configurable wait to 600 seconds preserved thresholds. The subsequent full gate passed with no incomplete checks. A real Groq completion (103 input / 64 output tokens) exported parent and inference spans over OTLP. Jaeger independently confirmed provider, model, usage and absent content. Failed attempt artifacts remain alongside the correction.

## 2026-10-26 — Phase 013 campaign ledger

- A campaign completion without usage must retain the pre-dispatch reservation; P03 includes a regression for this accounting rule so unknown usage cannot become zero in cumulative totals.
- The project full gate writes incident simulation and check artifacts and can start a Prometheus validator container when Docker is visible. This offline ledger phase hid Docker, skipped service integration, and restored the historical simulation/check outputs; the gate is accurately recorded as `INCOMPLETE`, with zero test failures.


## 2026-10-27 - Phase 014 exception event leakage

- Removing explicit `span.record_exception(exc)` did not remove private data: the OpenTelemetry context manager records exception events automatically when the wrapped function raises. Decorators now set `record_exception=False` and emit only an allowlisted category/status. A regression asserts no exception events or message/traceback content for both sync and async failures.

## 2026-10-27 - Phase 015 evidence destination

- `demo/service_trace.py` and `scripts/check_services.py` previously wrote service results to phase-009 files unconditionally. Added `P03_SERVICE_EVIDENCE_DIR`, constrained to the project's evidence subtree, and confirmed an outside path exits INCOMPLETE before Compose. The isolated recheck wrote only new phase evidence; all 134 pre-existing evidence files kept their exact SHA-256 and size.
