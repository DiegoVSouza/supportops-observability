# Phase 020 — Identify transient service-read failures

## Goal

Make P03 service-check failures attributable to a fixed endpoint class without exposing trace IDs or response data, and give idempotent local GETs a finite retry window longer than phase 019's 0.3 seconds.

## Acceptance criteria

1. Add tests proving every service-check read is labeled from a fixed allowlist and that trace IDs/query contents never appear in a raised error.
2. Bound transient GET behavior to at most five attempts with delays of 0.25, 0.5, 1.0 and 2.0 seconds; retain the five-second request timeout, and never retry HTTP errors or non-GET side effects.
3. Preserve phase 018 and 019 failed gates as immutable history. Do not replay their synthetic task IDs or provider/model calls.
4. Run focused, fast, full offline fake gate and one service-enabled full gate on the new committed checker candidate, with cached-only images, loopback-only ports, unique namespace, before/after protected hashes, exact cleanup and Docker reconciliation.
5. If service gate fails, retain INCOMPLETE, record the fixed endpoint category if available, clean only the exact namespace, and do not retry the gate.

## Scope

Only the local P03 service verification script and its tests change. This does not establish production exporter reliability, customer telemetry, model quality, approval or promotion.
