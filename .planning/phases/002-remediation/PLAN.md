# P03 Phase 002 Plan — Telemetry and gate remediation

## Task 1 — Lock lifecycle and gate regression contracts

Inspect current instrumentation, checks, alerts, and feature state. Add tests showing later setup calls cannot replace active configuration, flush/shutdown behavior, and nonzero full-gate behavior when a required validator is missing or fails. Test alert names against expression semantics.

## Task 2 — Complete telemetry lifecycle and metrics

Implement safe provider initialization and explicit flush/shutdown. Add task-type success, retry, error, and cost-per-request/task metrics with bounded-cardinality labels and privacy-safe attributes. Preserve current public instrumentation contracts or record ADR/versioning if change is unavoidable.

## Task 3 — Build deterministic integrated trace and alert evidence

Provide a deterministic fake/replay-boundary trace spanning API, queue, worker, agent, tool, and database, with correlation IDs. Add representative alert-series tests. Validate rules with `promtool` and exercise dashboards/incidents against the local stack when tools/services are available; accurately label missing stack gates INCOMPLETE.

## Task 4 — Reconcile feature state and run all gates

Populate feature checklist and progress from saved evidence. Run unit/contract, package, full gate, promtool, Compose and service/E2E checks where available. Save outputs and ensure the full gate is nonzero/INCOMPLETE for any required gate not executed.

## Path ownership

- `allowed_write_paths`: `.planning/phases/002-remediation/**`, `supportops_obs/**`, `tests/**`, `scripts/**`, `alerts/**`, `metrics/**`, `dashboards/**`, `incident-lab/**`, `demo/**`, `stack/**`, `instrumentation/**`, `docs/harness/feature_list.json`, `docs/harness/progress.md`, `docs/harness/failures.md`, `docs/architecture.md`, `docs/knowledge/**`, `README.md`, `README.pt-BR.md`, `artifacts/evidence/**`; package metadata/lockfiles only if a reviewed API/dependency change requires it.
- `forbidden_changes`: paths outside `projects/p03/**`; root lab, shared kit, sibling projects; secrets; weakened/deleted tests; public API/version changes without ADR and consumer plan; paid/live model calls; external publication, push, deploy, PR, merge, or production claims from synthetic data.

## Dependencies and execution mode

- Depends on phase 001 artifacts and current P03 package/stack configuration.
- `LLM_MODE=fake`; replay is conditional on traceable sanitized cassettes.
- Python and pinned OTel/Prometheus dependencies are local project inputs. Docker daemon and `promtool` are optional environment dependencies to verify at execution time, not assumed present.
- Consult official OTel/Prometheus documentation for changing APIs and record exact versions/sources in `docs/harness/sources.lock.json` if dependencies or conventions are changed.

## Checks

- `python scripts/check_fast.py` — if present; otherwise record the repository's equivalent fast unit command.
- `python -m pytest -q` — unit/contract tests.
- `python scripts/check_full.py` — full gate; must be nonzero/INCOMPLETE if required checks did not run.
- `promtool check rules alerts/observability.yml` — required when `promtool` is available; otherwise INCOMPLETE and full gate remains nonzero.
- `docker compose -f stack/docker-compose.obs.yml config` and local service/E2E checks — run when Docker is available; static parsing does not count as service E2E.
- Save command, exit code, and output under `artifacts/evidence/`, with gate type identified.

## Plan review

Reviewed against GSD-LITE-PLUS and P03 remediation acceptance: four observable tasks, tests precede implementation, local path ownership is explicit, dependencies are separated from required outcomes, and unavailable required checks cannot be silently counted as PASS. The plan is approved for execution.

## Stop condition

Stop before public API incompatibility without ADR/version/consumer plan. Do not claim stack E2E when required services or validators are unavailable; record INCOMPLETE and continue independent local work. Do not use live providers or production telemetry.
