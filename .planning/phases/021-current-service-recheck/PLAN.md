# Plan

1. Record current candidate, container/network/volume identities and normalized states; verify cached image identities, free loopback ports and an empty uniquely named Compose namespace.
2. Run one locked fake full service gate using the phase-owned evidence path, stop on failure, clean only that namespace and reconcile prior identities and states.

allowed_write_paths: `.planning/phases/021-current-service-recheck/**`, `artifacts/evidence/current-service-recheck-021/**`, `docs/harness/progress.md`, `docs/harness/feature_list.json`. forbidden_changes: source, previous evidence, unrelated Docker resources, images/tags, credentials, provider calls, external data and approvals.

Budget: USD 0, no provider calls, fake only. Validation: locked `scripts/check_fast.py` and `scripts/check_full.py`, unique `P03_COMPOSE_PROJECT`, phase-owned evidence directory, pre/post Docker inventories. Stop before startup if ports, cached images or namespace preflight fail; on any gate failure retain evidence and do not replay. Plan-check: self-assessment; independent review PENDING.
