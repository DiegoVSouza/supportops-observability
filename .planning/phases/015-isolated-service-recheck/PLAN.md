# Phase 015 plan

## Ownership

Allowed write paths:

- `.planning/phases/015-isolated-service-recheck/**`
- `demo/service_trace.py`
- `scripts/check_services.py`
- `artifacts/evidence/service-recheck-015/**`
- `docs/harness/progress.md`
- `docs/harness/failures.md`
- `docs/knowledge/P03-observability.md`

Forbidden changes:

- Compose definitions, ports override, collector configuration, dashboards, alert rules, runtime instrumentation outside the scenario output routing, campaign/eval data, historical artifacts, dependencies/locks, credentials, sibling repository source, and root lab files.
- Any existing Docker project/container/network/volume or cloud service.
- Provider/model calls, image build/pull, deployment, public listener, paid usage, or alert threshold changes.

## Tasks

1. Add evidence-directory routing for scenario, trace export, and alert output; validate offline checks and commit this candidate before starting services.
2. Confirm cached images, free configured ports, unique project namespace, and historical artifact hashes; run the actual synthetic service/trace/alert gate once under `p03-phase015-service`.
3. Clean only the phase project, reconcile Docker and historical artifact state, review evidence and staged paths, and record scoped gate status.

## Validation commands

- `uv run --locked python scripts/check_fast.py`
- `PYTHONPATH=. uv run --locked pytest -q --basetemp artifacts/evidence/service-recheck-015/offline-pytest tests`
- `docker compose -p p03-phase015-service -f stack/docker-compose.obs.yml -f artifacts/evidence/phase-008-compose.override.yml -f stack/docker-compose.integration.yml config --quiet`
- `P03_COMPOSE_PROJECT=p03-phase015-service P03_SERVICE_EVIDENCE_DIR=artifacts/evidence/service-recheck-015 ... uv run --locked python scripts/check_services.py`
- `docker compose -p p03-phase015-service -f stack/docker-compose.obs.yml -f artifacts/evidence/phase-008-compose.override.yml -f stack/docker-compose.integration.yml down --volumes --remove-orphans`
- `git diff --check`, staged-diff and secret review before commit.

## Budget and stop conditions

- Budget: USD 0; zero provider/model calls. Fake LLM only; no credentials except local placeholder values required by LocalStack.
- Stop before startup if any port is occupied, required image is missing, phase namespace is nonempty, historical output hash differs, or Compose config reaches an unexpected project/path.
- Stop on service failure, alert timeout, non-local endpoint, unexpected Docker identity change, secret exposure, or uncertain cleanup. Keep actual exit and output; do not repeat a semantic failure for a pass.
- Do not alter the candidate after service execution starts. Human, independent, dataset/rubric, and promotion reviews remain PENDING.
