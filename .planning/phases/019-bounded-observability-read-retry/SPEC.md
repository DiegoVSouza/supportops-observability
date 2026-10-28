# Phase 019 — Bound retries for transient observability reads

## Goal

Make the P03 service checker tolerate a transient connection close during idempotent local GET requests without masking HTTP errors or retrying service mutations/model calls.

## Acceptance criteria

1. Add red-first unit tests for a direct/wrapped connection disconnect followed by success, persistent disconnect bounded to three requests, and non-retryable HTTP status.
2. Retry only transient transport failures in the GET-only `fetch` helper, at most three total attempts with bounded short backoff; preserve auth headers, response parsing, and current HTTP status behavior.
3. Never replay `demo/service_trace.py`, Compose operations, provider/model calls, queue actions, or database writes from this helper.
4. Run locked focused, fast and full fake checks; then a single fresh isolated service-enabled full gate on the new committed candidate, with image/port/hash preflight, phase-only cleanup, and Docker identity reconciliation.
5. Record all statuses honestly; the earlier phase-018 `RemoteDisconnected` remains immutable. Human/independent/quality/promotion gates remain pending.

## Out of scope

Provider request retry, application task replay, any external network, alert thresholds, service endpoints, credentials, live customer traffic, and paid spend.
