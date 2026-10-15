# Phase 002: Integrated telemetry and reliable gates

## Goal

Complete P03's telemetry lifecycle, integrated trace/metric coverage, alert validation, and honest full-gate behavior while retaining privacy-safe defaults and stable public APIs.

## Baseline

- Phase 001 provides the observability package, synthetic incident fixtures, and a local full check.
- Current progress records unit checks and Compose static validation as PASS; `promtool` and live Docker stack E2E are INCOMPLETE because the validator and daemon were unavailable at that time.
- The portfolio remediation audit identifies telemetry setup mutation risk, incomplete integrated trace/metrics evidence, an alert validation gap, and an empty feature checklist.
- Current full-gate and dependency availability must be rechecked during execution; this baseline is historical, not a new run.

## Acceptance criteria

1. Telemetry initialization cannot mutate the active provider configuration through later setup calls; an explicit, tested flush/shutdown path exists.
2. A deterministic integrated trace covers API, queue, worker, agent, fake/replay LLM boundary, tool, and database, with correlation IDs and privacy-safe attributes. Integration gaps are reported accurately where dependencies are not available.
3. Metrics cover task success by task type, retries, errors, and cost per request/task. Alert names and expressions measure the same condition.
4. Prometheus rules are validated with `promtool` and representative alert series are exercised when available. If a required validator or stack gate did not run, the full gate exits nonzero and reports `INCOMPLETE`.
5. Provisioned dashboards and incident scenarios are exercised against a local stack before any dashboard/alert E2E claim. Synthetic data stays labeled synthetic; production metrics remain `PENDING`.
6. Feature checklist and progress accurately record executed PASS, INCOMPLETE, and PENDING gates.

## Constraints

- No paid/live LLM calls or external deployment.
- Preserve privacy-safe telemetry defaults; content capture remains opt-in.
- No public API incompatibility without ADR, package version update, and consumer update plan.
- No sibling-source imports or shared kit edits. No weakening tests.
- Separate unit, package integration, service integration, E2E, and agent evaluation.

## Out of scope

Production telemetry claims, production cost/latency metrics, cloud deployment, and changes to P01/P04/P05 contracts.
