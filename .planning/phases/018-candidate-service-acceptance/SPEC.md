# Phase 018 — Service acceptance for the span privacy candidate

## Goal

Verify the committed P03 phase-017 candidate through the isolated local HTTP/SQS/PostgreSQL/OTLP/Jaeger/Grafana/Prometheus path after the span-status privacy fix.

## Acceptance criteria

1. Freeze the exact candidate code revision before service startup; run only deterministic fake/local inputs and no Groq/provider completion.
2. Confirm all required image IDs are already cached, all declared loopback ports are free, the unique phase Compose namespace is empty, and historical project evidence hashes match before startup.
3. Run the service-enabled full project gate with all output routed under this phase's evidence directory; verify HTTP/SQS/worker/database/agent/fake-LLM stages, Jaeger traces, dashboard, and four existing synthetic alerts.
4. Clean only the phase-owned Compose project and reconcile container/network/volume identities plus historical evidence files; preserve unrelated stacks.
5. Record exact command outputs/exits and classify this as local synthetic service acceptance only. Production OTLP reliability, real model quality, human/independent review and promotion remain INCOMPLETE/PENDING.

## Constraints

No image build/pull, external listener, provider/credentials, paid spend, customer data, threshold/schema/campaign change, or unrelated service lifecycle. Stop before startup if ports/images/namespace/evidence do not satisfy preflight. Clean only `p03-phase018-span-status` if the phase started it.
