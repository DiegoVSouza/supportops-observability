# Phase 017 plan

## Execution controls

- `llm_mode`: `fake`; no credentials, provider, network, OTLP endpoint, Compose service lifecycle, or external service. The full check may perform read-only Docker readiness/config inspection and a single transient `docker run --rm` of the already-cached `prom/prometheus:v3.14.0` solely as a local rule validator; capture Docker container/network/volume identities before and after and require exact restoration.
- `allowed_write_paths`:
  - `.planning/phases/017-span-status-privacy/**`
  - `supportops_obs/instrumentation.py`
  - `tests/test_instrumentation.py`
  - `docs/architecture.md`
  - `docs/harness/progress.md`
  - `docs/harness/failures.md`
  - `docs/harness/feature_list.json`
  - `docs/knowledge/P03-observability.md`
  - `artifacts/evidence/span-status-privacy-017/**`
- `forbidden_changes`: historical campaign/dataset/rubric/live evidence; phases 014–016; exporter endpoints, capture policy, lock/dependencies, stack/dashboards/alerts, other projects/root lab, secrets, provider/network/Compose service operations, uncached image use, paid spend, publication/push, and weakened tests.
- Budget: USD 0; local CPU only.
- Stop if verification requires real OTLP/provider access, changes to capture/retention policy, dependency updates, or mutation of protected history.

## Tasks

1. Add failing sync and async span-status assertions for a synthetic private sentinel and record the red result.
2. Set `set_status_on_exception=False` on the P03 decorator spans; prove the SDK status description remains empty while error category, ERROR status and caller exception are preserved.
3. Run focused, fast and full fake checks; record exact commands/exits/output and update scoped docs. Review protected-path hashes and staged diff, scan for secrets, then commit atomically.

## Validation

- `uv run --locked --offline python -m pytest tests/test_instrumentation.py -q`
- `uv run --locked --offline python scripts/check_fast.py`
- `P03_CHECK_EVIDENCE_DIR=artifacts/evidence/span-status-privacy-017/run P03_SKIP_SERVICES=1 LLM_MODE=fake uv run --locked --offline python scripts/check_full.py` (permits only the cached one-shot promtool validator and read-only Docker config checks; service E2E is intentionally INCOMPLETE).
- Verify phase-014–016 evidence, all tracked artifacts outside the phase-017 evidence directory, datasets, campaign and stack files unchanged.
- `git -c core.whitespace=cr-at-eol diff --cached --check`; inspect staged names/diff; secret-pattern scan.

## Plan check

The next available phase is 017. Write paths are P03-local and exclude shared/locked histories and service configuration. Task count is three. This phase has no real provider or service effect; clean-context review remains PENDING.
