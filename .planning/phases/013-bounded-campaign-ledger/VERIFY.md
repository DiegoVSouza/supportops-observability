# Verify — Bounded campaign ledger for P03

Save commands, exit codes, and sanitized output in `artifacts/evidence/live-campaign-ledger/`.

- [ ] Ledger events are append-only, reserve before dispatch, retain unknown usage, and reject duplicate/uncertain trial replay.
- [ ] Cumulative requests/tokens/estimated cost are atomic across campaign IDs and parallel attempts.
- [ ] Local OS lease blocks a concurrent process and releases normally; metadata contains no trace or content fields.
- [ ] Resume inspection is read-only, content-free, rejects unknown/empty campaigns with exit 2, and never dispatches.
- [ ] Dry-run/blocked execution do not load exporter, provider, credential, network, Docker, or service state.
- [ ] Focused tests and fake/full project gates pass; previous telemetry reports and local service stacks are preserved.
- [ ] Decisions, failures, progress, evidence/report, and bilingual knowledge are updated; staged diff is reviewed and committed.
- [ ] Independent clean-context phase verification is recorded separately.

Campaign dispatch, resource/reviewer approval, model preflight, full telemetry campaign, canary, and rollback remain promotion gates.
