# Phase 016 — Historical-safe full P03 gate

Date: 2026-10-27

## Candidate and guard

Candidate: `489aaf9cfa24633cdceb20c8a2f948e9b230e910`. `P03_CHECK_EVIDENCE_DIR` routes the full-gate summary, Prometheus fixture, deterministic trace, and incident simulation to a project-evidence directory. The existing `P03_SERVICE_EVIDENCE_DIR` routes service traces and alerts to the same fresh directory. Both reject paths outside `artifacts/evidence/` before running checks. Guard rejection for `../outside-evidence` exited 1 before any test/service action.

## Full gate

Command: `P03_CHECK_EVIDENCE_DIR=artifacts/evidence/full-gate-016/run P03_SERVICE_EVIDENCE_DIR=artifacts/evidence/full-gate-016/run P03_COMPOSE_PROJECT=p03-phase016-full-gate LLM_MODE=fake PYTHONPATH=. uv run --locked python scripts/check_full.py`

Exit: 0; `check-full: PASS; failures=0; incomplete=0`.

- Fast/config/locked dependency checks: PASS.
- Locked tests: 50 passed.
- Deterministic integrated trace: PASS, 8 spans.
- Incident simulation: PASS, 3 incidents and 11 spans.
- Prometheus `check rules` and `test rules`: exit 0.
- Compose config: exit 0.
- Actual service integration: exit 0; HTTP/SQS/PostgreSQL workflow, three exported Jaeger traces, Grafana dashboard and all four existing synthetic alerts firing.
- Fake LLM only; no model/provider endpoint, `.env` credential, cloud service, paid spend, build, or image pull.

## Preservation and cleanup

The phase used `p03-phase016-full-gate` with cached image digests in `cached-images.json`. `down --volumes --remove-orphans` exited 0 and left no phase resources. Pre/post Docker inventories match for all 102 pre-existing container IDs, normalized states and image references; all 21 network identities, 89 volume names and image inventory match. All 160 pre-existing evidence files have identical path, size and SHA-256. The run directory contains the new gate outputs.

## Gate boundary

P03's local synthetic software gate is PASS. Groq quality/billing, production exporter reliability, customer-facing telemetry, human review, independent review and promotion remain PENDING/INCOMPLETE. No live quality or promotion claim is made.
