# P03 live-v1 operational observability rubric

## Scope

Evaluate operational telemetry and alert behavior using synthetic fixtures. The required provider/model identity is Groq `openai/gpt-oss-20b`. Language is not applicable. A future authorized provider call is capped at one request per scenario trial. No customer content, prompt, response, tool arguments, or message body may appear in exported spans, logs, or metric labels. The dataset and outcomes still require independent human review.

## Critical dimensions

- **Trace topology:** all expected spans share one trace ID and each child references the exact parent span ID.
- **Usage and identity:** exported provider, model, input/output token counts, and bounded metrics match the provider response exactly; missing or fabricated usage fails.
- **Privacy:** any content-bearing span attribute, log field, or metric label fails, including prompt/response/content/arguments/messages. Capture remains disabled.
- **Exporter operation:** outage errors are visible and bounded; after recovery, export succeeds and queue/flush behavior returns to healthy state.
- **Alert lifecycle:** applicable alert fires when its configured expression crosses threshold and resolves after the signal recovers. Existing thresholds may not be weakened.

A case passes only when every required assertion passes. Report results by operational family, split, and error type; retain all failures. Offline simulations are not real OTLP/provider/alert evidence. A holdout-driven change requires a fresh, separately authorized confirmation set before claiming generalization.
