# Phase 012 — Live campaign preparation

## Goal

Prepare P03's reviewed operational scenario set, telemetry assertions, and a no-provider reservation dry-run for the broad readiness campaign. This is an observability evaluation, not generic model answer scoring.

## Current evidence and constraints

- Revalidated repository HEAD: `05b02a5fc8421bd9b98512270eac3652b59c057e` (`feat(telemetry): export real Groq spans to local Jaeger`).
- P03's project budget is USD 0. Phase 010's single instrumentation request is a bounded free-plan exception; it does not authorize a multi-trial campaign.
- Prior local Docker acceptance evidence exists, but service/runtime health and ports must be rechecked before any future stack use. No Compose mutation is part of preparation.
- Prompt capture remains disabled. No credential access, provider request, raw prompt/response persistence, or alert threshold reduction is allowed.

## Acceptance criteria

1. A versioned set contains 30 unique telemetry/operational scenarios: 9 development and 21 sealed holdout. Required families include parent/child correlation, exact usage accounting, provider/model identity, content exclusion, exporter outage/recovery, and alert fire/recovery, with at least three cases per family.
2. Every case has operational preconditions, expected span/metric/alert observations, forbidden content attributes, applicability, rubric, criticality, and finite calls/tokens/time caps. Language is `NOT_APPLICABLE`; operational scenarios remain distinct.
3. Configuration includes three trials, at most one normal provider call per trial, cumulative caps, confirmation reserve, timeout/retry/chunk/pacing/wall-clock fields and approval source. Expanded capacity remains `PENDING`; the project budget stays zero.
4. Dry-run reports exact case/trial/call totals and unresolved reservations without SDK construction, credential reads, network, or Docker mutation. Generation fails closed until a finite reservation is approved.
5. Code-first checks reject incorrect trace correlation/model/provider/usage, any prompt/content attribute, unbounded exporter failure, or missing alert recovery. Offline simulations are never represented as real OTLP/provider evidence.

## Out of scope

Provider or Docker execution, production instrumentation claims, runtime/API changes, threshold relaxation, cross-project imports, cloud usage, credentials, publishing, or push.
