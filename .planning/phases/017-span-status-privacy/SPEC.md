# Phase 017 — Prevent exception text in span status

## Goal

Close a privacy gap in P03's real instrumentation decorators: OpenTelemetry's context manager may place an exception message in the span ERROR status description even when exception events are disabled.

## Acceptance criteria

1. Add red-first sync and async in-memory exporter regressions using a unique synthetic sentinel; assert status remains ERROR with an empty description and no event/attribute contains the sentinel.
2. Disable automatic exception status mutation at all P03 decorator span call sites while preserving the fixed error category, ERROR code, and original exception behavior.
3. Keep `record_llm_call` semantics, opt-in content capture, package dependencies, exporter settings, schemas, alerts, historical telemetry and campaign evidence unchanged.
4. Run focused instrumentation tests and project fast/full gates in the locked environment. Do not start, stop or inspect unrelated Docker stacks; if required cached validators are unavailable, report the gate INCOMPLETE with exact evidence.
5. Update P03 failure/progress/feature/architecture/knowledge and phase evidence; review secret-free staged diff and commit locally.

## Scope

This is a local SDK/in-memory privacy correction. It does not prove production OTLP privacy or reliability and does not authorize live generation, customer telemetry, human/independent review, or promotion.
