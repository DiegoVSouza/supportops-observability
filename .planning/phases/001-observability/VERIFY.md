# Phase 001 verification plan

## Unit

- Run package unit tests with `LLM_MODE=fake`; test setup idempotence, decorators, trace context, metrics, content privacy, malformed records, all loop signals, healthy paths, and boundaries.
- Validate incident fixtures and rule unit inputs with deterministic synthetic data; do not report them as model quality metrics.

## Integration

- Use in-memory OTel exporter to inspect nested spans, attributes, and trace IDs.
- Validate Prometheus rule syntax with `promtool` if present and parse Compose/Grafana configuration with installed tooling.
- P01 runner integration is INCOMPLETE until a built, installed package has version, source commit and artifact hash recorded.

## E2E

- Run demo in fake mode locally and verify expected telemetry output. Docker stack E2E is INCOMPLETE if Docker is unavailable; no external deployment.

## Agent evaluation

- Not applicable: this phase contains no autonomous agent or model. LLM calls are data passed into instrumentation tests only.

## Evidence

Save each command, exit code and captured output under `artifacts/evidence/`. Report live traces/screenshots as PENDING absent a real stack run. Keep unit, integration, E2E, and evaluation statuses separate.
