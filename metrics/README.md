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
| `supportops_tasks_by_type_total` | Counter | task_type, outcome | Task success/error count by bounded type (`billing`, `refund`, `technical`, `other`) |
| `supportops_task_cost_usd` | Histogram | task_type | Caller-reported cost distribution per task/request |
| `supportops_tool_retries_total` | Counter | tool | Caller-reported retries |
| `supportops_tool_retries_by_task_type_total` | Counter | tool, task_type | Retries by bounded task type |
| `supportops_agent_loop_signals_total` | Counter | reason | Repeated actions, state cycles, or step limit |

Do not add prompt, user, ticket, argument, model, or request IDs as metric labels. Use histogram quantiles for p50/p95; alerts and dashboards query these histogram buckets. Thresholds are illustrative until a service defines SLOs from real runs.

Task type is normalized to a fixed allowlist. Cost observations and task outcomes are caller-reported per completed task; they are not production measurements. The local API-to-database trace uses function doubles and an in-memory exporter and is explicitly synthetic.
