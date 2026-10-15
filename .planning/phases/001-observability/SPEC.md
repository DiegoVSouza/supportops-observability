# Phase 001: Observability foundation

## Goal

Deliver a safe, installable Python package for agent observability, with deterministic tests and local operational artifacts, preserving the intent of `specs/P03-agent-observability.md`.

## User-visible behavior

- Callers configure telemetry by service name, optional OTLP endpoint, and explicit content-capture opt-in.
- Decorators create spans for agents and tools. LLM records produce token, cost, latency, and error metrics without retaining content by default.
- Logs carry active trace/span identifiers. Loop detection flags repeated tool/argument sequences, state cycles, and step limits without flagging a healthy varied sequence.
- A local compose stack, Grafana dashboard, Prometheus alerts, three incident scenarios, and trace-oriented runbooks let an operator investigate symptoms.
- The demo uses a local runner double until the P01 wheel is built and installed with provenance. That real integration gate remains INCOMPLETE in this phase.

## Acceptance criteria

1. Unit tests prove span nesting/attributes, log correlation, privacy defaults and explicit capture, and LLM metric recording including malformed/negative inputs.
2. Loop detector tests prove all three patterns and a healthy sequence with no false positive, including boundary and reset behavior.
3. Prometheus rules pass `promtool check rules` when promtool exists; Compose YAML and Grafana JSON parse with available local tooling. Missing tools are reported INCOMPLETE.
4. Three deterministic incident scenarios and runbooks explain how to locate tool latency, loop, and cost anomaly in traces. Real screenshots/exports remain PENDING unless actually produced from a real run.
5. `scripts/check_full.py` runs real package tests, lint/type or structural checks selected for pinned dependencies, and configuration validation; it must not print a placeholder success.
6. English README and Portuguese README/knowledge docs include architecture, setup, API, dashboard/alerts, incident steps and interview answers in EN/PT.

## Constraints

- Python 3.11+, fake mode by default, no paid calls, no external deployment.
- Do not rely on evolving OpenTelemetry GenAI semantic conventions; record official sources and explicitly version any convention used.
- Do not import code using paths into sibling repositories.
- Content capture is opt-in and must be tested as disabled by default.
