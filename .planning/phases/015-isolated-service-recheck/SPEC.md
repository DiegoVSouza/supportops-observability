# Phase 015: Isolated trace and alert service recheck

## Objective

Revalidate the actual P03 loopback HTTP -> PostgreSQL/SQS worker -> installed P01/P04 adapters -> OTLP/Jaeger trace and Prometheus alert flow after phase 014, while keeping all generated output in new phase evidence.

## Scope

- Route service scenario and exported trace/alert JSON to a caller-selected evidence directory instead of overwriting phase-009 artifacts.
- Run the existing `scripts/check_services.py` under a unique Compose project with only P03-defined services and cached images.
- Use fake LLM behavior, local-only test credentials, and synthetic incidents; no model/provider endpoint.
- Capture exact commands/exits, source candidate, image IDs, free-port checks, Docker inventories, traces/alerts, and cleanup.

## Constraints

- No changes to Compose, telemetry collector config, dashboards, alert rules, historical evidence, datasets/rubrics, campaign data, or sibling source trees.
- Unique project `p03-phase015-service`, only P03 Compose resources, local test credentials, no image build/pull, no provider calls, no paid use, no cloud action.
- Use the existing isolated P03 service port mappings only after verifying all are free; preserve all existing Docker stacks.
- User, independent, dataset/rubric, and promotion reviews remain PENDING. A service pass is not a live quality or promotion pass.
