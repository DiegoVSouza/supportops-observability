# Phase 014 — Content-safe telemetry failures

Status: PLANNED. Offline implementation only; no provider, telemetry service, network, or Docker access.

## Goal

Prevent exception payloads from entering spans and make telemetry setup, flush, shutdown, and exporter failures report bounded operational status without propagating exporter failures into the instrumented application path.

## Context

- The actual package path is `supportops_obs.instrumentation`: decorators instrument real caller operations; `record_llm_call` records provider metadata, token counts, cost, latency, and optional content; `setup_telemetry` configures OTLP; public lifecycle functions flush and shut down the tracer provider.
- Current decorator failure handling calls `span.record_exception(exc)`. OpenTelemetry records exception message and stack, which can carry prompt, tool argument, or private data despite `capture_content=False`.
- `flush_telemetry` returns a boolean but provider exceptions escape. `shutdown_telemetry` also propagates shutdown errors. Setup may propagate OTLP exporter construction errors.
- P03 has a zero paid LLM/cloud budget. Tests will use fake providers/exporters and in-memory spans only. Existing live evidence and local stack configuration are immutable in this phase.

## Acceptance criteria

1. Sync and async instrumented exceptions preserve application behavior and span error status while exporting only a fixed, allowlisted error category; message, repr, traceback, arguments, and exception event fields are absent.
2. Telemetry exporter construction, flush, and shutdown failures are reflected through fixed-cardinality telemetry-health counters and boolean lifecycle results; failures do not leak exception messages or cause an instrumented operation to fail or replay.
3. Shutdown remains idempotent, flush timeout validation remains enforced, and a failed setup does not mark a usable exporter as successfully configured.
4. Offline tests exercise successful and failing setup/flush/shutdown/export paths with fake dependencies; no OTLP network endpoint is contacted.
5. Locked fast and full checks pass, or infrastructure service gates remain explicitly INCOMPLETE. Existing live traces, dataset, campaign ledger, alert rules, and Docker/service stacks remain byte-identical.
6. Documentation records failure visibility, content/privacy limits, and the absence of verified production service telemetry.

## Out of scope

Provider calls, real OTLP export, Docker/services, endpoint-policy redesign, data retention changes, prompt/response capture, metrics/alert thresholds, campaign execution, dataset/rubric/threshold changes, cloud/paid resources, other projects, or promotion.
