# Metrics contract

Metrics are defined in the canonical package at `supportops_obs/instrumentation.py` and exposed through `metrics_registry()`.

| Metric | Type | Labels | Meaning |
|---|---|---|---|
| `supportops_llm_calls_total` | Counter | provider, outcome | LLM call count |
| `supportops_llm_tokens_total` | Counter | kind=input/output | Caller-reported token counts |
| `supportops_llm_cost_usd_total` | Counter | none | Caller-reported cumulative cost |
| `supportops_llm_latency_seconds` | Histogram | none | Caller-reported LLM latency |
| `supportops_operation_calls_total` | Counter | kind, outcome | Agent/tool/database/HTTP call count |
| `supportops_operation_latency_seconds` | Histogram | kind, outcome | Instrumented operation duration |
| `supportops_agent_steps` | Histogram | outcome | Steps observed for a task |
| `supportops_tasks_total` | Counter | outcome | Task success/error count |
| `supportops_tool_retries_total` | Counter | tool | Caller-reported retries |
| `supportops_agent_loop_signals_total` | Counter | reason | Repeated actions, state cycles, or step limit |

Do not add prompt, user, ticket, argument, model, or request IDs as metric labels. Use histogram quantiles for p50/p95; alerts and dashboards query these histogram buckets. Thresholds are illustrative until a service defines SLOs from real runs.
