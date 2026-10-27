# Verify — Content-safe telemetry failures

Status: PLANNED. Store all command output and exits under `artifacts/evidence/content-safe-exporter-failures/`.

- [ ] Sync and async operation errors retain application exceptions/status while spans contain only allowlisted error categories and no message, repr, traceback, or exception event payload.
- [ ] Exporter construction, force-flush, and shutdown errors produce bounded telemetry health counters and safe boolean status, without escaping into caller business operations.
- [ ] Setup failure does not claim an exporter is configured; shutdown remains idempotent; invalid flush timeout remains rejected.
- [ ] Offline fake exporter/provider tests cover these failures without credentials, network, OTLP service, or Docker.
- [ ] Existing content-capture opt-in/default tests and LLM/agent spans still pass.
- [ ] Locked fast/full gates pass; any missing Docker/promtool/service integration is accurately reported INCOMPLETE.
- [ ] Pre-existing historical evidence, eval data/rubric/campaign ledger, alert/dashboard/stack files are byte-identical.
- [ ] Staged paths are phase-owned; diff and secret scan pass; local atomic commit is recorded.
- [ ] No production telemetry reliability, live campaign, or promotion gate is declared approved; independent/human review remains PENDING.
