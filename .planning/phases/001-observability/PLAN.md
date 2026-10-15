# Phase 001 execution plan

## Task 1 — Intake, contracts, and verification design

Complete profile rationale, public API shape, provenance requirements, architecture, and this phase's testable criteria. Review the plan for path ownership and dependency ordering before implementation.

## Task 2 — Instrumentation and loop detection

Implement package metadata and public API, OTel setup/decorators/LLM recording, correlated structured logging, deterministic loop detection, and behavior tests including failures and healthy traffic.

## Task 3 — Stack, rules, dashboards, and incident lab

Add Compose stack, Collector/Prometheus/Grafana provisioning, dashboards, alert rules, synthetic incident fixtures, and trace investigation runbooks. Validate locally available parsers and tools.

## Task 4 — Demo, docs, and gate

Replace the placeholder full check with real validation, add the demo runner double, English/Portuguese READMEs, knowledge doc, provenance lock, and saved command/exit/output evidence. Record the P01 package integration gate as INCOMPLETE.

## Ownership and execution controls

- `allowed_write_paths`: `harness.yaml`, `docs/harness/**`, `docs/architecture.md`, `.planning/phases/001-observability/**`, `supportops_obs/**`, `tests/**`, `instrumentation/**`, `stack/**`, `metrics/**`, `dashboards/**`, `alerts/**`, `incident-lab/**`, `demo/**`, `scripts/check_full.py`, `pyproject.toml`, lockfile, `README.md`, `README.pt-BR.md`, `docs/knowledge/**`, `artifacts/evidence/**`.
- `forbidden_changes`: kit files, root lab files, sibling projects, global Git config, external services, paid model calls, P01 contract changes.
- Contract: preserve P03 API (`setup_telemetry`, `traced_agent`, `traced_tool`, `record_llm_call`, `LoopDetector`); local demo double is not real integration.
- Dependencies: Python 3.11+; pin OTel and Prometheus dependencies and record official documentation sources. Docker and promtool are optional local validators and their absence is INCOMPLETE.
- LLM mode: `fake`.
- Validation: `python scripts/check_full.py`; additional optional `promtool check rules alerts/*.yml` and Docker Compose config validation when installed.
- Stop condition: stop before any public API incompatibility; add ADR/version and obtain consumer update plan first. Stop integration claims until P01 package artifact is available.

## Plan review

Reviewed before product implementation: four observable tasks, explicit project-only path ownership, stable API constraints, and clear P01 dependency gate. No product code is authorized before these phase artifacts are committed.
