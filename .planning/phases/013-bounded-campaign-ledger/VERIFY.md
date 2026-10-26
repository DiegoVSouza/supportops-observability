# Verify — Bounded campaign ledger for P03

Save commands, exit codes, and sanitized output in `artifacts/evidence/live-campaign-ledger/`.

- [x] Ledger events are append-only, reserve before dispatch, retain unknown usage, and reject duplicate/uncertain trial replay.
- [x] Cumulative requests/tokens/estimated cost are atomic across campaign IDs and parallel attempts.
- [x] Local OS lease blocks a concurrent process and releases normally; metadata contains no trace or content fields.
- [x] Resume inspection is read-only, content-free, rejects unknown/empty campaigns with exit 2, and never dispatches.
- [x] Dry-run/blocked execution do not load exporter, provider, credential, network, Docker, or service state.
- [x] Focused tests and deterministic checks pass. Full check has zero failures but is `INCOMPLETE` because Docker/promtool validators and service integration were intentionally not executed in this phase.
- [x] Previous telemetry reports and service stacks are preserved; decisions, failures, progress, evidence/report, and bilingual knowledge are updated.
- [x] Staged paths and diff are reviewed, and the implementation is locally committed.
- [ ] Independent clean-context phase verification is recorded separately.

Campaign dispatch, resource/reviewer approval, model preflight, full telemetry campaign, canary, and rollback remain promotion gates.
