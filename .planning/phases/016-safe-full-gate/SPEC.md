# Phase 016: Historical-safe full P03 gate

## Objective

Run P03's full offline and service-enabled project gate while directing every deterministic demo, simulation, service trace/alert, rule fixture, and gate summary to new phase evidence.

## Scope

- Add a configurable, project-evidence-confined output directory to `scripts/check_full.py`, `demo/integrated_trace.py`, and `incident-lab/simulate.py`.
- Reuse `P03_SERVICE_EVIDENCE_DIR` from phase 015 for service output, pointing it at the same fresh phase run directory.
- Run `check_full.py` with fake mode, cached images, and a new isolated Compose project; do not run provider/model endpoints.
- Commit the source candidate before the full gate; capture historical evidence hashes and Docker inventories before/after.

## Constraints

- Do not edit or overwrite existing evidence, campaign/eval data, datasets/rubrics, alert rules, dashboards, service Compose definitions, dependencies, credentials, sibling source, or root lab files.
- Docker validation containers and services must use cached images only, no build/pull. Run only the P03 services under `p03-phase016-full-gate` with existing loopback ports after availability checks.
- No provider/model calls, external cloud, paid spend, public listener, Terraform, deploy, or human review claim.
- User, independent, dataset/rubric, and promotion reviews remain PENDING.
