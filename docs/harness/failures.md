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

## 2026-10-27 - Phase 016 full-gate evidence destination

- The project full gate, integrated-trace demo, and incident simulator each wrote into fixed historical evidence paths. Added `P03_CHECK_EVIDENCE_DIR`, constrained to `artifacts/evidence/`, and verified an outside path fails before checks. The full service gate then passed using a new run directory; all prior 160 evidence files remained byte-identical.

## 2026-10-27 - Phase 017 automatic exception status description

- Disabling `record_exception` did not prevent the OpenTelemetry context manager from automatically setting ERROR status description to `RuntimeError: <message>` when sync or async decorated work raised. A synthetic sentinel reproduced the leak in both in-memory spans. Decorator spans now use `set_status_on_exception=False` and set a generic ERROR status plus a fixed error category themselves; caller exceptions remain unchanged. Production OTLP privacy remains unverified.

## 2026-10-27 - Phase 018 transient Jaeger query disconnect

- The service-enabled full gate started the isolated seven-service stack and `demo/service_trace.py` completed all three synthetic tasks. The subsequent `check_services.py` Jaeger read exited INCOMPLETE with `RemoteDisconnected`; the exact request site was not identified in the gate output. Later bounded read-only diagnostics returned HTTP 200 for Jaeger service/trace endpoints, Grafana dashboard search, and Prometheus alerts, but did not perform the missing stage assertions. The failed gate was not replayed. Cleanup of the exact phase Compose namespace passed and all pre-existing container/network/volume identities and 216 tracked artifact hashes were preserved. A future phase may add a bounded retry for idempotent read-only Jaeger GETs, then use a fresh candidate and service run.
