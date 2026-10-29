# Plan

1. Record Docker daemon, image, port and exclusive namespace preflight without lifecycle changes.
2. If preflight passes, run the owning locked fake service gate in the exclusive namespace and reconcile resource identities; otherwise record the specific missing prerequisite.

allowed_write_paths: `.planning/phases/023-service-availability-recheck/**`, `artifacts/evidence/service-availability-recheck-023/**`, `artifacts/evidence/service-availability-recheck-023-tmp/**`.

forbidden_changes: source, existing resources, images, unrelated artifacts, volumes, credentials, provider calls, customer data, paid use and external effects. Fake only, zero calls / USD 0. max_tries: 3 per failure. Stop before startup if daemon, image, ports or namespace unavailable; no Docker gateway assumption. Plan-check is implementer self-assessment.
