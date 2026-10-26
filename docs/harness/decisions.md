# Intake decisions

- Objective: ship `supportops_obs`, an installable Python observability package for agent workflows with OpenTelemetry spans, correlated logs, metrics, and deterministic loop detection.
- Success criteria: behavior tests cover nested spans and trace correlation, LLM token/cost/latency recording, privacy opt-in, loop patterns and healthy traffic; Prometheus rules validate; the Compose config and dashboard parse; full validation exits zero in fake mode.
- Pattern: workflow instrumentation library, not an autonomous agent. The demo runner is a local contract double until P01's versioned package is explicitly installed.
- Runtime rationale: Python 3.11+ library built on OpenTelemetry API/SDK and Prometheus client. No model calls are required; `LLM_MODE=fake` is the default.
- Risk: telemetry can contain private prompts and tool arguments. Capture is disabled by default, opt-in, and sensitive attributes are excluded unless explicitly enabled. No multi-tenancy or external communication.
- Budget: zero paid LLM and cloud budget. Phase 010 uses only the explicitly permitted Groq free-plan allowance for a single instrumentation run.
- External integration: P01 package is not currently an installed dependency; P01 integration gate remains INCOMPLETE until package version, source commit, and artifact hash are recorded.
- API compatibility: use stable OpenTelemetry tracing/metrics APIs; do not claim vendor GenAI semantic conventions as stable. Record official source and version findings in `docs/harness/sources.lock.json`.
- Phase 010 decision (2026-10-26): make one synthetic Groq completion in an opt-in evaluation to validate real LLM span/token/latency instrumentation. Keep prompt capture disabled, use free-plan allowance only, and leave billed cost `PENDING` until confirmed. No product provider runtime is enabled by this evaluation.

## 2026-10-26 — Live Docker acceptance

Use opt-in Groq live mode with numbered credentials and authenticated model preflight. Preserve deterministic fake defaults and fail closed on provider/contract failures. Only local synthetic acceptance and the designated free allowance are authorized; billed cost remains PENDING. Evidence: artifacts/evidence/live-docker/.
