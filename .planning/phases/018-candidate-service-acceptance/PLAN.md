# Phase 018 plan

## Execution controls

- `llm_mode`: `fake`; zero provider calls, credentials, external network, OTLP endpoint or paid spend.
- `allowed_write_paths`:
  - `.planning/phases/018-candidate-service-acceptance/**`
  - `artifacts/evidence/span-status-service-018/**`
  - `docs/harness/progress.md`
  - `docs/harness/failures.md`
  - `docs/harness/feature_list.json`
  - `docs/knowledge/P03-observability.md`
- Product source, locked dependencies, alerts/dashboards/Compose configuration, datasets/rubrics/campaigns, prior evidence, and all sibling/root files are frozen. No service or other Docker namespace may be targeted.
- Budget: USD 0; local synthetic service only. Images must be cached at the expected IDs from phase 016. Compose service ports are loopback only.
- Stop if any required image is missing/different, port is occupied, phase namespace is nonempty, historical evidence hash differs, output escapes the phase-owned evidence directory, non-fake mode is observed, or an unrelated Docker identity changes. On started phase resources, cleanup only with the exact phase Compose project and verify cleanup.

## Tasks

1. Freeze candidate `24f4d2b78fff09322c6fa286a08da8d27be55b71` (product source hash) and capture preflight: locked environment, cache image IDs, loopback port occupancy, phase namespace, all prior evidence hashes, and read-only Docker identities. Record the plan check and preflight before startup.
2. Run the full service-enabled locked project gate once with `P03_CHECK_EVIDENCE_DIR=artifacts/evidence/span-status-service-018/run`, `P03_SERVICE_EVIDENCE_DIR=artifacts/evidence/span-status-service-018/run`, `P03_COMPOSE_PROJECT=p03-phase018-span-status`, `LLM_MODE=fake`, and bounded alert wait. Inspect only metadata, stage names, status codes and required alert names from evidence.
3. Clean the exact phase namespace if it was started; reconcile historical hashes and all Docker resource identities. Update progress/features/knowledge and verification, review staged paths and secret scan, then commit locally.

## Validation commands

- `uv run --locked --offline python scripts/check_fast.py`
- Read-only `docker image inspect` for all seven expected images and read-only listener check for ports 24317, 24318, 24686, 24319, 29090, 23000, 37432 and 34566.
- `docker compose -p p03-phase018-span-status -f stack/docker-compose.obs.yml -f artifacts/evidence/phase-008-compose.override.yml -f stack/docker-compose.integration.yml config --quiet`
- `P03_CHECK_EVIDENCE_DIR=artifacts/evidence/span-status-service-018/run P03_SERVICE_EVIDENCE_DIR=artifacts/evidence/span-status-service-018/run P03_COMPOSE_PROJECT=p03-phase018-span-status LLM_MODE=fake uv run --locked --offline python scripts/check_full.py`
- Cleanup only the exact phase namespace with the same `docker compose -p p03-phase018-span-status ... down --volumes --remove-orphans` command if it was started; reconcile after state.
- Secret scan, staged diff inspection, and `git -c core.whitespace=cr-at-eol diff --cached --check`.

## Plan check

Three tasks, concrete project-local paths, exact fake-mode command and project namespace, cached-image/port/hash preflight, safe cleanup and stop conditions are defined. This is a service acceptance check, not production exporter, model quality or promotion evidence. Independent/human review remains PENDING.
