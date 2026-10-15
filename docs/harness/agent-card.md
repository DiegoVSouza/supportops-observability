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
