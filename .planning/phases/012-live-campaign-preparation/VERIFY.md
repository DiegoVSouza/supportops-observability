# Verify — Live campaign preparation

Use repository artifacts and commands, not implementation-chat claims. Save each command, exit code, and sanitized output in `artifacts/evidence/live-campaign-preparation/`.

- [x] Validator and tests confirm 30 unique scenarios, 9 development / 21 fixed holdout, six required families with five scenarios each. Holdout access is not technically restricted; independent outcome review remains pending.
- [x] All cases use `NOT_APPLICABLE`; duplicate source groups and cross-split reuse are rejected.
- [x] Cases specify operational preconditions, expected observations, privacy exclusions, rubric, criticality, applicability, and finite provider/token/time caps.
- [x] Focused tests reject trace/parent correlation, provider/model identity, usage, content attribute, exporter outage/recovery, and alert lifecycle failures.
- [x] Config records three trials, one-request task caps, 90 primary / 60 confirmation calls, timeout, zero retries, chunking, pacing/wall-clock fields, and USD 0 source. Unresolved cumulative caps remain PENDING.
- [x] `-S` dry-runs for pilot, development, and holdout report 6 / 27 / 63 calls and primary 90-call maximum with zero-budget blockers, without credential, SDK, network, or Docker access.
- [x] Non-dry-run exits `INCOMPLETE` before provider dispatch; campaign generation is disabled, retries are zero, and there is no fallback.
- [x] Seven focused tests, `check_fast`, and all 39 unit tests pass with saved command/exit evidence. Docker-mutating full/service gates were intentionally not run in this phase.
- [x] Simulator provenance is rejected as live OTLP evidence; no live/provider/production claim is made.
- [x] Staged paths are within phase ownership; reviewed diff has no credentials or unrelated user data.


## Outstanding phase gates

- Independent case/rubric reviewer: `PENDING`.
- Clean-context phase verification: `PENDING`.
- Durable cumulative request/token ledger and campaign lease: `NOT IMPLEMENTED`.
- Budget/quota, cumulative caps, confirmation funding, pacing, wall-clock cap, and authenticated catalog preflight: `PENDING`; generation remains disabled.
- Docker service health and local stack acceptance are out of scope for preparation and must be rechecked in their own approved phase.
