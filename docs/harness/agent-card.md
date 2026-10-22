# Agent Card — P03 Synthetic Demo

## Product identity

P03 is an observability library, not a production autonomous agent. This card describes only the local synthetic demo used to validate trace shape.

## Demo behavior

- Input: fixed ticket identifier `T-SYNTHETIC`.
- Flow: local API function → local queue function → local worker function → triage function → fake LLM record → ticket lookup tool → database function.
- Failure case: the first in-memory database call raises a synthetic timeout; the tool wrapper records one retry and the second call succeeds.
- Output: deterministic fixture ticket status and billing classification.
- Telemetry: in-memory exporter with a fixed trace ID; each span is labeled synthetic.

## Boundaries and status

No network API, durable queue, separate worker, live model, MCP tool, or database service is used. The trace proves only local span nesting and metric updates. Service integration and dashboard/alert E2E remain `INCOMPLETE`; production outcomes and metrics remain `PENDING`.

## Phase 008 local service observation

An isolated Docker stack also received one explicitly synthetic OTLP trace over the local collector and exposed it in Jaeger with seven spans (API, queue, worker, agent, fake LLM, tool, database). Prometheus scraped only the synthetic exporter, and Grafana provisioned the SupportOps dashboard. This validates local telemetry transport and dashboard provisioning; it does not represent the product's API, durable broker, worker, or database. Promtool validated the rules and a representative alert fixture. The live synthetic rule run reached `firing` for all four alert rules, including the two with a five-minute hold. Full service acceptance remains `INCOMPLETE`; real model, cost, latency, and quality measurements remain `PENDING`.

## 2026-10-22 — Executable service acceptance

Phase 009 replaces the service trace double with loopback HTTP, LocalStack SQS, the installed P04 worker and P01 core runner, and PostgreSQL operations. All three deliberately synthetic incidents were exported to Jaeger; no real model or customer content is used.

## Phase 009 verified service evidence

The local full gate uses a loopback HTTP service, LocalStack SQS, P04 0.1.3 worker, P01 0.1.1 agent, and PostgreSQL. Three synthetic incidents were queried from Jaeger, the provisioned dashboard was found, and four synthetic alert rules reached firing. `uv run --locked python scripts/check_full.py` exited 0. The explicit `P03_SKIP_SERVICES=1` run exited 2 with INCOMPLETE. Production signals and model evaluation remain PENDING.
