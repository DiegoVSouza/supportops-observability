# Phase 019 plan

## Execution controls

- `llm_mode`: `fake`; zero provider calls, secrets, external network or paid spend.
- `allowed_write_paths`:
  - `.planning/phases/019-bounded-observability-read-retry/**`
  - `scripts/check_services.py`
  - `tests/test_check_services.py`
  - `docs/architecture.md`
  - `docs/harness/progress.md`
  - `docs/harness/failures.md`
  - `docs/harness/feature_list.json`
  - `docs/knowledge/P03-observability.md`
  - `artifacts/evidence/span-status-read-retry-019/**`
- `forbidden_changes`: span instrumentation, exporter configuration, datasets/rubrics/campaigns/live evidence, alert rules/dashboards/Compose files, package/lock/dependencies, other projects/root, provider/model retry, external/public listener, paid spend, push/publication, weakened tests.
- Budget: USD 0. Local service stack only under `p03-phase019-read-retry`; cached image IDs must match phase 016; only loopback ports may be exposed.
- Stop before startup if preflight fails. On a service gate failure, record once and do not repeat the gate. Clean only the exact phase Compose project and reconcile tracked artifacts and Docker resources.

## Tasks

1. Add red-first fake-opener tests for one transient direct and wrapped disconnect, persistent disconnect capped at three GETs, and HTTP errors not retried.
2. Implement a maximum-three-attempt GET transport retry with fixed backoff no greater than 0.2 seconds per wait. Keep HTTP errors non-retryable and do not change mutation or model paths.
3. Run locked focused/fast/full fake checks and a fresh service-enabled full gate after committing the candidate; capture preflight, outputs and cleanup, update docs, review diff/secrets, commit verification.

## Validation commands

- `uv run --locked --offline python -m pytest tests/test_check_services.py -q`
- `uv run --locked --offline python scripts/check_fast.py`
- `P03_CHECK_EVIDENCE_DIR=artifacts/evidence/span-status-read-retry-019/offline P03_SKIP_SERVICES=1 LLM_MODE=fake uv run --locked --offline python scripts/check_full.py` (expected exit 2 solely for intentionally skipped service gate)
- After candidate commit: recheck all seven cached phase-016 image IDs, eight loopback ports, unique project empty, and tracked artifact hashes; run `P03_CHECK_EVIDENCE_DIR=artifacts/evidence/span-status-read-retry-019/run P03_SERVICE_EVIDENCE_DIR=artifacts/evidence/span-status-read-retry-019/run P03_COMPOSE_PROJECT=p03-phase019-read-retry P03_ALERT_TIMEOUT_S=600 LLM_MODE=fake uv run --locked --offline python scripts/check_full.py` once.
- On failure, clean only `p03-phase019-read-retry`, reconcile 102/21/89 inventories and all protected hashes, then stop.
- Secret scan, staged path review and CRLF-aware staged diff check.

## Plan check

Three tasks and precise write paths are defined. Retry is restricted to read-only telemetry GETs and three total attempts. Application, queue and provider actions are never retried here. Service gate is one-shot on a fresh candidate with exact namespace, cached-only images and an explicit stop/cleanup rule. Independent review remains PENDING.
