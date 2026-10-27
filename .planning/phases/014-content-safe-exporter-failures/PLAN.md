# Plan — Content-safe telemetry failures

## Execution controls

- `llm_mode`: `fake`; in-memory/fake exporters only. No credentials, network, OTLP endpoint, or provider. For required full validation, read-only Docker identity/config inspection and a transient `--rm` local Prometheus validator container are permitted only when its image is already cached; no Compose service lifecycle is permitted.
- `allowed_write_paths`:
  - `.planning/phases/014-content-safe-exporter-failures/**`
  - `supportops_obs/instrumentation.py`
  - `tests/test_instrumentation.py`
  - `tests/test_live_groq_eval.py`
  - `docs/architecture.md`
  - `docs/harness/progress.md`
  - `docs/harness/failures.md`
  - `docs/harness/feature_list.json`
  - `docs/knowledge/P03-observability.md`
  - `artifacts/evidence/content-safe-exporter-failures/**`
- `forbidden_changes`: `harness.yaml` budget, frozen live dataset/rubric/campaign/ledger, historical live traces and reports, alert rules/dashboards/stack, credential files, dependencies/lock, sibling repositories, root lab/harness-kit, provider calls, external network/services, Compose `up/down/restart`, container stop/remove, uncached image pull, content capture changes, paid usage, publication/push, or weakened tests. Capture before/after container and Compose project identities around full validation.
- Budget: zero provider calls/tokens and USD 0 cloud/exporter spend. Local CPU only.
- Validation: focused instrumentation tests; locked fast/full gates with `P03_SKIP_SERVICES=1`; read-only `docker ps -a`/`docker compose ls` snapshots; cached-image check before allowing the transient `docker run --rm prom/prometheus:v3.14.0` validator; byte hashes for all pre-existing artifacts/evaluation/campaign/stack files; `git diff --check`; staged path/secret review. Record commands, exits, output and infrastructure skip status under the phase evidence directory.
- Stop conditions: a change requires live OTLP/Docker/provider access, broader metric policy or alert threshold changes, lock/dependency updates, or edits to historical evidence; retain the affected item as INCOMPLETE.

## Tasks

1. **Test content leakage and exporter failures first** — add red sync/async exception assertions for absence of exception messages/events and lifecycle tests for constructor/flush/shutdown failures, idempotence, error counters, and product-path isolation.
2. **Implement typed failure telemetry** — replace raw exception recording with allowlisted categories; add bounded-cardinality telemetry export failure counters and fail-soft lifecycle results without exposing exception strings.
3. **Verify and record operational limits** — run focused and full locked offline checks, preserve historical artifacts and project stacks, update progress/failures/feature/knowledge, save evidence, inspect staged diff, and commit locally.

## Plan check

Implementer self-check against P03's current runtime, locked OpenTelemetry packages, phase 013 live-campaign isolation, project zero-budget decision, and existing instrumentation API. Next available phase ID is 014. Write paths exclude telemetry stack, campaign, and historical evidence. No provider/network/service interaction is permitted or needed. Independent clean-context review remains PENDING.
