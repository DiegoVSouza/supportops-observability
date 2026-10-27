# Phase 016 plan

## Ownership

Allowed write paths:

- `.planning/phases/016-safe-full-gate/**`
- `scripts/check_full.py`
- `demo/integrated_trace.py`
- `incident-lab/simulate.py`
- `artifacts/evidence/full-gate-016/**`
- `docs/harness/progress.md`
- `docs/harness/failures.md`
- `docs/knowledge/P03-observability.md`

Forbidden changes:

- Existing evidence outside the new phase directory, evaluation/campaign state, prompts, rubrics/datasets, alert rules/dashboards, Compose/collector configuration, locks, credential files, sibling projects/source, and root lab/kit.
- Existing Docker resources outside this phase's uniquely named project; image build/pull, provider calls, external systems, cloud actions, paid spend, and public listeners.

## Tasks

1. Route gate/deterministic output under a validated evidence directory, run fast and offline suite, check existing-output and outside-path refusal, then commit the candidate.
2. Confirm all required images are cached, all service ports are free, phase namespace is empty, and historical evidence hashes match; run the full project check with phase-owned service and output paths.
3. Clean only the isolated project, reconcile all pre-existing Docker and artifact identities, review output/secrets/staged paths, and record scoped gate status.

## Validation commands

- `uv run --locked python scripts/check_fast.py`
- `PYTHONPATH=. uv run --locked pytest -q --basetemp artifacts/evidence/full-gate-016/offline-pytest tests`
- `P03_CHECK_EVIDENCE_DIR=../outside-evidence uv run --locked python scripts/check_full.py` (must refuse before checks)
- `P03_CHECK_EVIDENCE_DIR=artifacts/evidence/full-gate-016/run P03_SERVICE_EVIDENCE_DIR=artifacts/evidence/full-gate-016/run P03_COMPOSE_PROJECT=p03-phase016-full-gate LLM_MODE=fake PYTHONPATH=. uv run --locked python scripts/check_full.py`
- `docker compose -p p03-phase016-full-gate -f stack/docker-compose.obs.yml -f artifacts/evidence/phase-008-compose.override.yml -f stack/docker-compose.integration.yml down --volumes --remove-orphans`
- `git diff --check` and staged-diff/secret review before commit.

## Budget and stop conditions

- Budget: USD 0; zero provider/model calls; fake runner only; no image build/pull. Local test placeholders only for LocalStack.
- Stop before startup if any loopback port is occupied, required image digest differs/is missing, phase namespace is nonempty, historical artifact hashes differ, or output routing could target outside `artifacts/evidence/`.
- Stop on a gate failure, alert deadline, non-local route, secret, unexpected Docker identity change, or uncertain cleanup. Record actual output/exit, preserve all prior evidence, and do not repeat a semantic failure for a pass.
- Do not modify the candidate after full gate startup. Human/independent/dataset/rubric/promotion review remains PENDING.
