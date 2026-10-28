# Progress

- Intake and profile completed for `p03-agent-observability`.
- Phase 001 SDD artifacts authored and plan reviewed before product implementation.
- Tasks 002–004 implemented: package/tests, stack/dashboard/alerts, incident fixtures/simulation, fake runner demo, bilingual docs, source lock, and executable full check.
- Unit and in-memory exporter integration: PASS (21 tests; exact output in `artifacts/evidence/check-full.txt`).
- Docker Compose static config: PASS. Prometheus rule parser (`promtool`) and live Docker stack E2E: INCOMPLETE because promtool is absent and Docker daemon is unavailable.
- Real P01 runner integration: INCOMPLETE pending an approved, versioned package artifact. Synthetic incident traces and model quality are not production evidence.
- Local commits: `d9bb809` Git audit, `33eccaf` SDD contract, `abbb8fb` instrumentation/loop package, `7d78bf6` input/detector hardening, `a3373b5` stack/demo/docs/wheel.
- Phase 002 planning committed as `f892644`.
- Phase 002 targeted unit regression: PASS (15 tests; `artifacts/evidence/phase-002-regression-green.txt`). Full unit suite: PASS (26 tests; `artifacts/evidence/phase-002-unit.txt`). The red-first test result is retained in `phase-002-regression-red.txt`.
- Telemetry setup now preserves first-call provider and content-capture configuration; explicit `flush_telemetry` and `shutdown_telemetry` APIs are covered by unit tests.
- Full-check policy returns exit code 2 and `INCOMPLETE` when a required validator or dashboard/incident service E2E did not run. Current run: exit 2, with `promtool` unavailable and dashboard/incident service E2E not run; Docker Compose config and `uv lock --check` passed. Docker CLI 29.1.3 is present, but the daemon is unavailable. See `artifacts/evidence/check-full.txt`, `phase-002-check-full-exit.txt`, and `phase-002-docker-info.txt`.
- Prometheus rule validation, local stack service E2E, approved P01 integration, and production/model metrics remain INCOMPLETE/PENDING. Synthetic fixtures are not production evidence.
- Public package `0.2.0` includes the additive lifecycle API. Wheel build and isolated consumer import passed; commit/hash and P05 consumer-update requirement are recorded in `docs/harness/sources.lock.json` and `artifacts/evidence/package-consumer-update.md`. The wheel is local and unpublished.
- Phase 002 local commits: `f892644` planning, `41af3f7` lifecycle/gate remediation, and `dd321da` versioned wheel/provenance.
- Synthetic integrated-trace regression: PASS (2 tests, `artifacts/evidence/phase-002-integrated-green.txt`); full unit suite: 28 passed. The fake trace has 8 spans with fixed trace ID `00000000000000000000000000000042` and one instrumented transient DB failure/retry. `check_full.py` runs the trace and stores `artifacts/evidence/integrated-trace-synthetic.json`.
- Added bounded task-type success/error, per-task cost, and retry metrics. `docs/harness/agent-card.md` describes the demo as a local function-double flow; network services, durable queue/worker, and database integration remain `INCOMPLETE`.
- A deterministic synthetic trace now covers local API→queue→worker→agent→fake LLM→tool→database functions with a fixed trace ID and one recorded synthetic retry. This is package-level fake evidence, not service E2E. New task-type outcome, per-task cost, and retry-by-task-type metrics use bounded labels.
- Phase 003 fixed operation metric decorators raising `AttributeError` when the configured tracer returns `NonRecordingSpan`; outcome is now tracked in control flow for sync and async operations. Regression: red reproduced, 13 instrumentation tests pass, full suite 29 passed. Full gate remains INCOMPLETE (promtool and service E2E not executed). See `artifacts/evidence/phase-003-nonrecording-red.txt`, `phase-003-nonrecording-green.txt`, and `phase-003-full-gate.txt`.
- P05's isolated-wheel failure is covered by a consumer smoke against the 0.3.1 wheel: `traced_operation("database", "tickets.add")` returns successfully with the default non-recording tracer. The new wheel is recorded in `sources.lock.json`; P05 must consume 0.3.1. Service-backed gates remain INCOMPLETE.
- Phase 008: Dockerized Prometheus 3.14.0 `promtool check rules` and representative alert-rule test passed (outputs in `artifacts/evidence/phase-008-prometheus-rules.txt` and `phase-008-promtool-alert-test.txt`). The isolated Prometheus/Grafana/Jaeger/OTel stack is healthy; synthetic metrics scrape is up; Grafana dashboard provisioning and a seven-span synthetic OTLP trace were queried successfully. The two immediate synthetic alerts fired; error-rate and latency rules were still pending when captured. `check_full.py` returned exit 2 with zero failures and two incomplete required gates, so full acceptance remains INCOMPLETE. Product service tracing, incident workflow acceptance, P01 package integration, and production model/cost/latency evidence remain INCOMPLETE/PENDING.

## 2026-10-22 — Executable service acceptance

Phase 009 executes Docker promtool syntax and all four rule tests, real HTTP/SQS/P04-worker/P01/PostgreSQL incident traces, dashboard and live alerts. Full gate passed (31 tests, exit 0). Explicitly omitting the required service gate returned INCOMPLETE/exit 2. Production model metrics remain PENDING.

## 2026-10-22 — Phase 009 executable acceptance

- Docker promtool validated the alert file and all four alert fixtures. The full gate passed with P01 0.1.1 and P04 0.1.3 installed wheels, service traces, three synthetic incident cases, dashboard, and four live synthetic alerts.
- `P03_SKIP_SERVICES=1` returned exit 2 and `INCOMPLETE` with no failures; omission of a required gate cannot pass.
- Current proof: `artifacts/evidence/phase-009-full-gate-v013-final.txt`, `phase-009-full-gate-v013-detail-final.txt`, `phase-009-jaeger-export.json`, `phase-009-live-alerts.json`.
- Production traces and model quality remain PENDING; no production run was performed.

## 2026-10-26 — Phase 010 real LLM instrumentation

- Added optional Groq 1.7.0 live evaluation and enabled capability evals. The real response recorded model, provider, token usage, latency and estimated token cost in the existing instrumentation with content capture disabled.
- Final four-key run passed: 103 input / 82 output tokens, 0.420243 s, estimated cost USD 0.000032325; billed cost `PENDING`. All 31 focused tests passed. Full validation is incomplete only because Docker and promtool are unavailable.

## 2026-10-26 — Live evaluation readability cleanup

- Separate model catalog lookup, completion, retry timing, telemetry assertions and artifact writing into named local functions.
- Full offline gate: INCOMPLETE (31 tests pass; promtool and Docker service validation unavailable).
- Offline helper and static checks passed; no live calls were needed. Evidence: artifacts/evidence/code-cleanup/.

## 2026-10-26 — Live Docker acceptance

The first Docker gate exceeded its cold-start synthetic-alert wait. All four alerts later fired; increasing the configurable wait to 600 seconds preserved thresholds. The subsequent full gate passed with no incomplete checks. A real Groq completion (103 input / 64 output tokens) exported parent and inference spans over OTLP. Jaeger independently confirmed provider, model, usage and absent content. Evidence: artifacts/evidence/live-docker/.
## 2026-10-26 — Phase 013 bounded campaign ledger

- Added P03-local append-only reservations, atomic cumulative caps, a cross-process lease, and content-free read-only resume inspection. Unknown usage remains reserved; attempts are not replayed.
- Focused checks passed: 6 ledger tests and 8 campaign preparation tests. Fast check passed. Full gate returned 2 (`INCOMPLETE`) with zero failures because Docker/promtool validators and service integration were intentionally skipped; deterministic tests/eval/simulation/lock checks passed.
- Groq dispatch, authorized finite limits/reviews, crash recovery, live-path lease integration, and clean-context review remain pending. No provider or telemetry service call occurred. Evidence: `artifacts/evidence/live-campaign-ledger/`.

## 2026-10-27 - Phase 014 content-safe exporter failures

- Removed automatic and explicit OpenTelemetry exception events from the sync/async decorators. Failures keep the original exception behavior and span ERROR status while adding only a fixed allowlisted error category; exception text, traceback, prompt, and argument values are not exported.
- Telemetry setup now reports exporter-construction failure as `False`; flush and shutdown return safe boolean status and increment a fixed-cardinality failure counter. Shutdown remains idempotent. Focused tests pass (18); full gate has 50 passing tests and zero failures.
- Docker/Prometheus rule validation and Compose config passed using the already-cached local image; `P03_SKIP_SERVICES=1` intentionally leaves service integration INCOMPLETE (full-gate exit 2). P03 container identities and Compose projects were unchanged and already exited before/after. One unrelated container status field changed across read-only inventory snapshots; no command targeted other stacks.
- Pre-existing artifact files were restored byte-for-byte after full checks. No provider, OTLP service, external network, paid spend, or service lifecycle operation was used. Independent review and production exporter reliability remain PENDING. Evidence: `artifacts/evidence/content-safe-exporter-failures/`.

## 2026-10-27 - Phase 015 isolated real service recheck

- Routed synthetic HTTP/SQS traces, Jaeger export, and alert snapshots to a phase-owned evidence directory, protecting historical phase-009 output. Output paths outside `artifacts/evidence/` are rejected before Compose starts.
- Actual local integration passed: HTTP task ingress, PostgreSQL/SQS worker, installed P01/P04 adapters, three Jaeger traces with required stages, Grafana dashboard, and four synthetic Prometheus alerts firing. Runner used fake LLM behavior; no provider was contacted.
- Offline suite passed 50 tests; fast and Compose config checks passed. 134 prior evidence files remained byte-identical. Docker remained at 102 containers, 21 networks, and 89 volumes after phase cleanup; prior container identities/states, network IDs, and volume names matched.
- The P03 service scenario is PASS, but the service-enabled full project gate, model quality/account limits, and human/independent/promotion reviews remain INCOMPLETE/PENDING. Evidence: `artifacts/evidence/service-recheck-015/`.

## 2026-10-27 - Phase 016 historical-safe full gate

- Routed all deterministic full-gate, incident simulation, and integrated-trace output to a fresh `P03_CHECK_EVIDENCE_DIR` under the evidence tree. Outside paths fail before any gate checks. The phase-015 service evidence routing is reused for trace/alert output.
- Candidate `489aaf9cfa24633cdceb20c8a2f948e9b230e910` passed the complete service-enabled `scripts/check_full.py`: 50 tests, Prometheus rule check/test, synthetic traces/incidents, service traces/dashboard/four alerts, Compose config, and `uv lock --check`; exit 0, zero incomplete checks.
- All 160 pre-existing evidence files remained byte-identical. Docker returned to 102 containers, 21 networks, 89 volumes; all pre-existing IDs, normalized states, images, network and volume identities matched, and phase namespace is empty. Cached images only; no provider/model call.
- This is local synthetic acceptance, not Groq quality/billing, customer telemetry, independent/human review, or promotion approval. Those remain PENDING/INCOMPLETE. Evidence: `artifacts/evidence/full-gate-016/`.

## 2026-10-27 - Phase 017 span status privacy

- Red tests showed that OpenTelemetry automatically copied exception messages into sync and async span ERROR status descriptions even though exception events were disabled. P03-owned decorators now disable automatic status mutation and apply a generic ERROR code with the existing fixed error category; the original exceptions still propagate unchanged.
- In-memory regressions pass (19 focused tests); fast check passes. Full fake gate passes its 52 tests, Prometheus rule checks, Compose config and lock check with zero failures. Exit 2 is accurately INCOMPLETE because service integration was explicitly skipped.
- Full gate output was isolated under `artifacts/evidence/span-status-privacy-017/run/`; cached Prometheus validator image digest was `sha256:5ce7540c3c00ef4ab0c9d2c995c6a5b9c421f44b4a115d97a2c7af3b1c21cbb0`. Docker inventories returned 102 containers, 21 networks and 89 volumes; IDs/names/images/projects, network IDs and volume identities were unchanged. An unrelated existing `gossett_backend` container's restart-age field advanced between snapshots; no operation targeted it.
- No provider, credentials, OTLP endpoint, customer data, paid spend or Compose service lifecycle was used. Production exporter privacy/reliability, live model quality, review and promotion remain INCOMPLETE/PENDING. Evidence: `artifacts/evidence/span-status-privacy-017/`.
