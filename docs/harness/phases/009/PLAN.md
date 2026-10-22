# PLAN — Complete remaining authorized local remediation

allowed_write_paths: supportops_obs/**; demo/**; scripts/**; tests/**; stack/**; alerts/**; artifacts/**; docs/**; pyproject.toml; uv.lock; README.md; README.pt-BR.md

forbidden_changes: root roadmap, sibling source imports, shared kit changes, unrelated preexisting files/stacks, test weakening, external deploy/publish/push/PR/merge, Terraform apply, live/paid LLM.

llm_mode: fake

dependencies: Docker daemon and isolated local PostgreSQL/pgvector, Redis, LocalStack, Prometheus/Grafana/Jaeger/OTel; existing locked tools and approved P00–P04 wheels. Verify variable APIs in official docs and sources.lock.json.

## Observable tasks
1. Pin and verify the existing approved P01 wheel and add red tests for validator fallback and all alert rules.
2. Implement service demo and executable Docker rule/service gates with fail-closed dependency checks.
3. Run unit, package and local service gates and reconcile docs/evidence.

## Checks
Fast gate before each commit; meaningful red/green tests for changed behavior; unit/contract, package integration, service integration and E2E evidence separately; full gate and staged diff/secret review. Clean-context final verification follows the configured Builder review.

## Stop condition
Stop only the affected check for an unavailable dependency and save INCOMPLETE evidence; continue independent implementation. Leave cassettes/live/external-identity acceptance PENDING/INCOMPLETE. Do not claim external exactly-once from the local ledger.

## Plan review
Reviewed before code: four or fewer observable tasks; owned paths and package boundaries explicit; real-service and negative authorization checks included; public changes scoped in ADR; no missing gate can silently pass.
