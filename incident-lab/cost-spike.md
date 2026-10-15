# Incident: cost spike

1. Follow `LLMCostAnomaly` to the relevant time range.
2. Compare `supportops_llm_cost_usd_total`, token counts, request rate and task success rate.
3. Use traces grouped by service and provider to locate the call or loop associated with the increase; model identifiers are span-only and never metric labels.
4. Verify provider pricing metadata outside telemetry before estimating per-request cost. This package records caller-supplied cost; it does not price models.

The committed fixture is synthetic. A real exported trace and screenshot are PENDING.
