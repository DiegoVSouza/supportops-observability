# Phase 020 plan

## Execution controls

- `llm_mode`: `fake`; no provider/model calls, credentials, external network or paid spend.
- `allowed_write_paths`:
  - `.planning/phases/020-read-endpoint-diagnostics/**`
  - `scripts/check_services.py`
  - `tests/test_check_services.py`
  - `docs/architecture.md`
  - `docs/harness/progress.md`
  - `docs/harness/failures.md`
  - `docs/harness/feature_list.json`
  - `docs/knowledge/P03-observability.md`
  - `artifacts/evidence/span-status-endpoint-diagnostics-020/**`
- `forbidden_changes`: provider/model retry, application/queue/database replay, product instrumentation, endpoints/ports/credentials, packages/lock, datasets/rubrics/campaigns/historical evidence, Compose/alerts/dashboards, other projects/root, public exposure, paid spend or publication.
- Budget: USD 0. Local fake service path under the unique `p03-phase020-read-diagnostics` project; exact cached image identities and loopback-only ports required.
- Stop before startup on preflight mismatch. Run exactly one service-enabled gate for this candidate. On failure, preserve it, clean only the phase namespace and stop.

## Tasks

1. Add red-first tests for endpoint-class allowlisting, five-attempt cap/backoff and no trace-ID leakage; retain the phase-019 no-HTTP-retry behavior.
2. Update `fetch` with fixed read-endpoint labels and bounded delays (0.25/0.5/1/2 seconds); include only the allowlisted label and attempt count in exhausted transport errors.
3. Run locked tests/gates, freeze candidate, perform image/port/namespace/artifact preflight, run the one service gate, clean/reconcile, update scoped docs, review and commit.

## Validation

- `uv run --locked --offline python -m pytest tests/test_check_services.py -q`
- `uv run --locked --offline python scripts/check_fast.py`
- `P03_CHECK_EVIDENCE_DIR=artifacts/evidence/span-status-endpoint-diagnostics-020/offline P03_SKIP_SERVICES=1 LLM_MODE=fake uv run --locked --offline python scripts/check_full.py`
- After code commit: confirm seven cached phase-016 image IDs, free ports 24317/24318/24686/24319/29090/23000/37432/34566, empty phase namespace, and all tracked artifact hashes before startup.
- `P03_CHECK_EVIDENCE_DIR=artifacts/evidence/span-status-endpoint-diagnostics-020/run P03_SERVICE_EVIDENCE_DIR=artifacts/evidence/span-status-endpoint-diagnostics-020/run P03_COMPOSE_PROJECT=p03-phase020-read-diagnostics P03_ALERT_TIMEOUT_S=600 LLM_MODE=fake uv run --locked --offline python scripts/check_full.py`
- Cleanup only the phase namespace; reconcile Docker and tracked artifact identities. Secret scan and staged diff checks.

## Plan check

Three tasks, precise paths, cached-only local services, no provider/side-effect retry, a finite 3.75-second backoff window and one-shot failure policy are specified. Previous failure artifacts remain immutable. Independent/human review remains PENDING.
