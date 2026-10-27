# Phase 015 — Isolated P03 service recheck

Date: 2026-10-27

## Candidate and boundaries

Source candidate: `436ef8e746bea7c2747c9774ec844e546ce61e6b`. The only product-path changes route synthetic service, Jaeger, and alert outputs to `P03_SERVICE_EVIDENCE_DIR`, constrained to `artifacts/evidence/`; no tracing payload, privacy behavior, alert threshold, service, dataset, campaign, or dependency changed. An outside path was rejected before Compose.

Runner used `LLM_MODE=fake`; all AWS values were test placeholders for phase-local LocalStack. No model/provider, credential file, internet service, paid action, image build/pull, or cloud endpoint was used.

## Results

- `uv run --locked python scripts/check_fast.py`: exit 0, PASS.
- `PYTHONPATH=. uv run --locked pytest -q --basetemp artifacts/evidence/service-recheck-015/offline-pytest tests`: exit 0, 50 passed.
- Isolated Compose config: exit 0.
- Required P03 images were all cached at the recorded digests in `cached-images.json`; all eight configured loopback ports were verified free.
- `docker compose -p p03-phase015-service ... up --pull never -d --wait`: exit 0; seven phase-owned services became healthy.
- `P03_COMPOSE_PROJECT=p03-phase015-service P03_SERVICE_EVIDENCE_DIR=artifacts/evidence/service-recheck-015 LLM_MODE=fake uv run --locked python scripts/check_services.py`: exit 0. Three synthetic incidents passed the HTTP -> SQS/PostgreSQL worker -> installed P01/P04 adapter path. Jaeger returned three exported traces with required stages; Grafana dashboard was found; `AgentLoopDetected`, `LLMCostAnomaly`, `AgentErrorRateHigh`, and `LLMp95LatencyHigh` all reached firing under their existing alert windows.
- Phase Compose `down --volumes --remove-orphans`: exit 0.

## Preservation

All 134 pre-existing evidence files have matching path, size, and SHA-256 before/after. Docker stayed at 102 containers, 21 networks, and 89 volumes; all pre-existing container identities/normalized states, network IDs, and volume names match. The seven phase containers and phase network were removed; the phase namespace is empty.

## Remaining gates

This phase passes the local synthetic service/trace/alert recheck. It does not claim the service-enabled full project gate, live model quality/cost, provider quota, production exporter reliability, human review, independent review, or promotion. Those remain INCOMPLETE/PENDING. Evidence outputs are limited to synthetic traces and alerts in this directory.
