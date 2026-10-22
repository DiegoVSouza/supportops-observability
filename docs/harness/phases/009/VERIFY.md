# VERIFY � Executable observability acceptance

| Layer | Command | Exit | Evidence | Status |
| --- | --- | ---: | --- | --- |
| Unit, packages, Docker promtool, all four rule tests, real local services/three incidents | uv run --locked python scripts/check_full.py | 0 | artifacts/evidence/phase-009-full-gate-v013-detail-final.txt; phase-009-full-gate-v013-final.txt; phase-009-jaeger-export.json; phase-009-live-alerts.json | PASS |
| Required service omission | P03_SKIP_SERVICES=1 uv run --locked python scripts/check_full.py | 2 | artifacts/evidence/phase-009-fail-closed-detail.txt; phase-009-fail-closed.txt | PASS fail-closed behavior; run INCOMPLETE |
| Model quality/cost/comparable latency | Not authorized or cassette-backed | � | sources.lock.json | PENDING |
