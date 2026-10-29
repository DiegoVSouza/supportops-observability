# Plan

1. Implement P03-owned accounted telemetry adapter using injected fixture sessions, durable request reservations and the shared envelope/receipt contract.
2. Test usage, parent/child trace correlation, privacy with content capture enabled, malformed receipts, uncertain restart and no retry; run locked focused/fast/full gates with isolated evidence and exclusive service namespace after inventories.

allowed_write_paths: .planning/phases/024-accounted-telemetry/**; supportops_obs/accounted.py; tests/test_accounted.py; artifacts/evidence/accounted-telemetry-024/**; docs/harness/progress.md.
forbidden_changes: historical artifacts, existing Docker resources, sibling source imports, production/live credentials or calls, budgets, manifests, model/provider fallback, weakened tests and human approval. Fake mode, zero provider calls and USD 0 paid. max_tries: 3 per failure across sessions. Service lifecycle only after explicit ownership/inventory/ports/image checks, cleanup only phase-owned resources. Stop on uncertainty or unrelated-resource mismatch. Plan-check: implementer self-assessment.
