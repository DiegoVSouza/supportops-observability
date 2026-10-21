# PLAN — Prometheus and local observability service gates

## Allowed write paths
artifacts/evidence/**; docs/harness/**; docs/harness/phases/008/**; (product code only if a gate exposes a correctness defect, then stop and write a separate implementation task)

## Forbidden changes
No external deployment/publication, no live LLM, no changes to other repositories or shared kit, no weakening tests, no edits to root roadmap.

## Dependencies
Docker CLI/daemon and image pull availability; existing P03 dependencies; official Prometheus v3.14.0 image already pinned; isolated project name and host ports.

## Observable tasks
`n- 1. Run and save rule validation and alert tests. `n- 2. Run isolated stack and verify Prometheus/Grafana provisioning and alert data when feasible. `n- 3. Exercise fail-closed full gate and full checks. `n- 4. Reconcile feature/progress/agent/docs/matrix using only saved evidence.

## Checks
Dockerized promtool check rules; representative rule unit tests; Compose config and isolated services/dashboard/alert verification if viable; forced unavailable-validator full-gate behavior; full local gate.

## Stop condition
Stop service claims at the first unavailable required service/validator and record INCOMPLETE with command, exit code, output.

## Review
Plan reviewed before execution: scope is evidence-first, tasks are observable, path ownership is explicit, and unavailable services cannot become PASS.
