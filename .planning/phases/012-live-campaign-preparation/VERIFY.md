# Verify — Live campaign preparation

Use repository artifacts and commands, not implementation-chat claims. Save each command, exit code, and sanitized output in `artifacts/evidence/live-campaign-preparation/`.

- [ ] Exactly 30 distinct operational cases exist, 9 development and 21 sealed holdout; every required family has at least three scenarios.
- [ ] Language is `NOT_APPLICABLE`; scenario/source groups do not leak across splits.
- [ ] Cases specify expected spans, provider/model/usage, content exclusions, alert/export behavior, applicability, rubric and finite caps.
- [ ] Graders reject incorrect correlation or identity, usage mismatch, any content capture, unbounded exporter failure and missing alert recovery.
- [ ] Config includes three trials, per-request and cumulative ceilings, confirmation reserve, retry/timeouts/chunk/pacing/wall clock, and source of budget approval.
- [ ] Dry-run has no credential/SDK/network/Docker access and shows pilot 6 / full 90-call ceilings plus zero-budget blockers.
- [ ] Generation fails before dispatch while any approved quota/spend/cap is missing; no fallback or silent retry occurs.
- [ ] Safe offline checks pass and evidence includes command and exit code; Docker-mutating service checks are deferred to their authorized phase.
- [ ] No real provider/OTLP/alert result or production claim is inferred from simulation.
- [ ] Staged paths are allowed and contain no secrets or unrelated user data.
