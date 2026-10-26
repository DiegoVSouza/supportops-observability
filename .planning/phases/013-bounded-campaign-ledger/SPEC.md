# Phase 013 — Bounded campaign ledger for P03

## Goal

Add project-local durable reservations, a serialized local campaign lease, and read-only resume inspection for P03's operational telemetry campaign. Keep the campaign entirely offline and blocked until finite resource limits, independent reviews, and model preflight are evidenced.

## Starting evidence

- Phase 012 freezes 30 synthetic operational scenarios (9 development / 21 holdout), all with language `NOT_APPLICABLE`; the campaign plans 6 pilot calls, 90 primary calls, 60 fresh confirmation calls, or 156 additive calls.
- P03 measures OTLP traces, exact usage, exporter recovery, and alert lifecycle. Prompt capture and raw provider content remain disabled.
- The profile and decisions authorize USD 0 for broad campaign usage. Free-tier quota, cumulative limits, confirmation funding, reviewer sign-off, pacing, wall-clock ceiling, and model preflight remain pending.
- Prior phases in other repositories provide design precedent only. P03 owns its ledger and makes no cross-project accounting claim.

## Acceptance criteria

1. SQLite journal records pre-dispatch reservations and append-only outcomes; missing usage/content keeps the full reservation and a trial cannot be repeated after uncertain dispatch.
2. Request/token/estimated-cost caps are enforced atomically across P03 campaign IDs and concurrent attempts.
3. OS lease blocks concurrent P03 campaigns and releases normally. Lease and resume metadata contain no prompt, response, tool argument, trace payload, or credential.
4. `--resume CAMPAIGN_ID --dry-run` inspects sanitized operational records read-only, rejects unknown/empty campaigns with exit 2, and never retries an uncertain attempt.
5. Dry-run and blocked execution do not initialize telemetry exporters, Docker, provider SDK, credentials, or network. Generation remains blocked while any approval/resource field is unresolved.
6. Focused ledger tests and the P03 offline/full gates pass; historical trace artifacts and service stacks remain unchanged.

## Out of scope

Groq dispatch, exporter/service changes, Docker or Jaeger/Prometheus/Grafana mutation, content capture, quota/budget approvals, edits to frozen scenarios, cross-project accounting, public deployment, or external effects.

## Status

`PLANNED`; broad campaign and local-live promotion remain `INCOMPLETE`.
