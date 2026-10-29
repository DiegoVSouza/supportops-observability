# Accounted local operation with service telemetry

Enable the fixed synthetic P03 operation under the migrated four-call allocation. Require committed source/configuration/manifest before credentials, shared lease, durable local reservation before provider startup, authenticated model catalog and no retry/fallback. Export content-free correlated spans for at most one real call, reconcile both ledgers, query that trace without resubmission, and preserve prior service failures.
