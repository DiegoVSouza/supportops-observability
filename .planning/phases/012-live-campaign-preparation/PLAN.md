# Plan — Live campaign preparation

## Execution controls

- `llm_mode`: `fake`; planning, dataset validation and dry-run are offline.
- `allowed_write_paths`:
  - `.planning/phases/012-live-campaign-preparation/**`
  - `evals/datasets/live-v1/**`
  - `evals/rubrics/live-v1/**`
  - `evals/live-campaign.json`
  - `scripts/run_live_campaign.py`
  - `tests/test_live_campaign_preparation.py`
  - `docs/harness/decisions.md`
  - `artifacts/evidence/live-campaign-preparation/**`
- `forbidden_changes`: telemetry package/runtime, dashboards/alerts/thresholds, prior service/live evidence, other repositories, harness-kit, root `.env`, secrets, provider calls, Docker start/stop, public deployment, or paid/cloud usage.
- Budget source: P03 decisions authorize USD 0; phase 010's one-request free-tier allowance is historical and task-specific. Expanded campaign and fresh confirmation reservations are `PENDING`. Keys do not multiply quota.
- Planned load to display, not authorization: pilot 6 development scenarios × 1 trial = at most 6 normal provider calls; full set 30 × 3 = at most 90 calls before additional confirmation. Since project budget is zero, live generation is blocked pending explicit reconciliation.
- Validation: P03 fast check; dataset uniqueness/family/split tests; deliberate telemetry grader failures; dry-run isolation and blocked-generation tests. Do not run service-mutating full checks during this planning commit. Record command, exit code and sanitized output in the evidence path.
- Stop condition: stop before provider or Docker execution if quota, spend/budget, local stack ownership/ports, reviewer coverage, case review, model preflight, or any cap is unresolved. Mark missing service evidence `INCOMPLETE`.

## Tasks

1. **Freeze the operational scenarios and rubrics** — inspect current telemetry schemas, alert definitions and privacy controls; author 30 unique cases with the 9/21 split, six required families, `NOT_APPLICABLE` language and synthetic-only inputs.
2. **Add dry-run and reservation manifest** — validate campaign stages and config; report exact planned calls and `PENDING` fields without SDK construction, credential access, network, or Docker. Block generation until explicit finite capacity is approved.
3. **Prove telemetry grader and preparation controls** — test trace/model/provider/usage assertions, prompt-content exclusion, exporter failure/recovery and alert lifecycle with deliberate negative outcomes; run safe offline checks and save sanitized evidence.

## Plan review

Coordinator review completed against P03's zero-budget decision, telemetry/privacy contracts, and portfolio requirements. The 9/21 split, 6-call pilot, 90-call full ceiling, and `NOT_APPLICABLE` language are consistent. The plan keeps service mutations out of the planning commit and preserves existing stack state. Accepted for preparation execution on 2026-10-26. A clean-context verifier is still required for finished phase gates.
