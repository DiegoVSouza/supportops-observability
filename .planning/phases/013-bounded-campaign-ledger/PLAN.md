# Plan — Bounded campaign ledger for P03

## Execution controls

- `llm_mode`: `fake`; no provider, network, telemetry service, or Docker access in this phase.
- `allowed_write_paths`:
  - `.planning/phases/013-bounded-campaign-ledger/**`
  - `scripts/campaign_ledger.py`
  - `scripts/run_live_campaign.py`
  - `tests/test_campaign_ledger.py`
  - `tests/test_live_campaign_preparation.py`
  - `docs/harness/decisions.md`
  - `docs/harness/failures.md`
  - `docs/harness/progress.md`
  - `docs/knowledge/live-campaign-ledger.md`
  - `artifacts/evidence/live-campaign-ledger/**`
- `forbidden_changes`: root `.env`, frozen dataset/rubric/campaign approvals, telemetry runtime/configuration, historic Docker/service evidence, sibling repositories, harness-kit, prompt/response capture, provider/network/Docker/service calls, budget increase, public deployment, external effects, or push.
- Budget: profile paid budget remains USD 0. Free-tier campaign quota and cumulative request/token/spend/time caps remain `PENDING`; no call is authorized by the earlier one-request instrumentation acceptance.
- Validation: focused ledger tests, `-S` CLI help/dry-run/blocked execution, P03 fast/full fake gates, and evidence with exact exits.
- Stop condition: no Groq dispatcher, trace exporter, or service lifecycle code in this phase. Any unresolved limit/review leaves status `INCOMPLETE`.

## Tasks

1. **Test reservations, privacy, and concurrency first** — append-only event history, unknown usage retention, no reruns, atomic caps, cross-process lease, and content-free output.
2. **Implement P03-owned ledger and inspection** — add SQLite state and OS lease; wire read-only resume to the campaign CLI while preserving disabled generation and keeping observability services untouched.
3. **Verify offline isolation and document limits** — run focused and full fake gates, save command output, preserve prior artifacts, update decisions/failures/progress/knowledge, and review the staged diff.

## Plan review

Reviewed against P03 Phase 012, its privacy requirements, operational scenario rubric, and the portfolio readiness SPEC. The new paths do not own telemetry runtime, Docker stacks, or datasets. USD 0 and unresolved free quota remain unchanged; no provider or service call is in scope. Accepted for offline execution on 2026-10-26. Independent clean-context verification remains pending.
