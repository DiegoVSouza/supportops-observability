# VERIFY — Prometheus and local observability service gates

## Verification record
Populate below after each gate. Keep layers separate and retain failing or incomplete output.

| Layer / requirement | Command | Exit code | Evidence path | Status |
| --- | --- | ---: | --- | --- |
| Prometheus v3.14.0 rule syntax | `docker run --rm --entrypoint promtool -v C:/estudo/Golpe/lab/projects/p03/alerts:/rules:ro prom/prometheus:v3.14.0 check rules /rules/observability.yml` | 0 | `artifacts/evidence/phase-008-prometheus-rules.txt` | PASS |
| Prometheus rule unit test | `docker run --rm --entrypoint promtool -v C:/estudo/Golpe/lab/projects/p03/alerts:/rules:ro -v C:/estudo/Golpe/lab/projects/p03/artifacts/evidence/phase-008-alert-rules.test.yml:/tests/rules.test.yml:ro prom/prometheus:v3.14.0 test rules /tests/rules.test.yml` | 0 | `artifacts/evidence/phase-008-promtool-alert-test.txt` | PASS (representative loop alert) |
| Isolated Compose stack | `docker compose -p p03-remediation -f stack/docker-compose.obs.yml -f artifacts/evidence/phase-008-compose.override.yml up -d` | 0 | `artifacts/evidence/phase-008-stack-restart.txt; artifacts/evidence/phase-008-compose-config-current.txt; artifacts/evidence/phase-008-compose-ps.txt` | PASS (all published ports bound to 127.0.0.1; first attempt retained as `phase-008-compose-up-first-attempt.txt`) |
| Prometheus and synthetic scrape target | `curl.exe --fail-with-body http://127.0.0.1:29090/-/healthy` and `/api/v1/targets` | 0 | `artifacts/evidence/phase-008-prometheus-runtime.txt` | PASS; target up |
| Grafana dashboard provisioning and Jaeger service/trace query | `curl.exe --fail-with-body --user "$($env:GRAFANA_USER):$($env:GRAFANA_PASSWORD)" http://127.0.0.1:23000/api/search?query=SupportOps`; Jaeger `/api/services` and `/api/traces?service=p03-phase-008-synthetic` | 0 | `artifacts/evidence/phase-008-dashboard-jaeger.txt` | PASS (synthetic dashboard/trace; local credentials redacted) |
| Live synthetic alert rules | `curl.exe --fail-with-body http://127.0.0.1:29090/api/v1/alerts` | 0 | `artifacts/evidence/phase-008-prometheus-runtime.txt` | PASS (all four synthetic alerts firing) |
| Fail-closed full gate | `uv run --project . --locked python scripts/check_full.py` | 2 | `artifacts/evidence/phase-008-full-gate-summary.txt; artifacts/evidence/phase-008-full-gate-run.txt; artifacts/evidence/check-full.txt` | INCOMPLETE; failures=0, incomplete=2 (host promtool absent; structural gate does not execute dashboard/incident service E2E) |
| Gate fail-closed unit regression | `uv run --locked pytest tests/test_gate_status.py -q` | 0 | `artifacts/evidence/phase-008-gate-status-test.txt` | PASS |

## Review checklist
- [x] Exact command, exit code, and stdout/stderr are saved.
- [x] Service-backed claims identify the real service and version.
- [x] Full gate fails closed for required gates that did not run.
- [x] State/docs/matrix match evidence; PENDING is retained for model/cost/latency without valid runs.
- [x] Git staged diff is limited to this task and contains no secrets.
