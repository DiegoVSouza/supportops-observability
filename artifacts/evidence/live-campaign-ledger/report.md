# Phase 013 — P03 bounded telemetry campaign ledger

Status: `INCOMPLETE`. Offline ledger tests pass. The broad campaign is not authorized, and the project full gate reports intentional service-validator omissions.

## Evidence

| Command | Exit | Result |
|---|---:|---|
| `uv run --locked python -m unittest discover -s tests -p test_campaign_ledger.py -v` | 0 | 6 ledger tests passed. |
| `uv run --locked python -m unittest discover -s tests -p test_live_campaign_preparation.py -v` | 0 | 8 telemetry campaign preparation and grader tests passed. |
| `uv run --locked python scripts/check_fast.py` | 0 | Required project metadata gate passed. |
| `uv run --locked python scripts/check_full.py` with Docker hidden and `P03_SKIP_SERVICES=1` | 2 | Zero failures; status `INCOMPLETE` because promtool, Docker Compose validation, and service integration were not run. Deterministic unit, eval, incident simulation, and lock checks passed. |
| `uv run --locked python -S scripts/run_live_campaign.py --help` | 0 | Stage and read-only resume options are documented. |
| `uv run --locked python -S scripts/run_live_campaign.py --stage pilot --dry-run` | 0 | Offline reservation summary only; no provider, credential, network, Docker, or service access. |
| `uv run --locked python -S scripts/run_live_campaign.py --stage pilot` | 2 | Campaign remains blocked by pending review, quota, caps, and preflight. |

The full check's historical output and incident-simulation artifact were restored after capturing this phase's output. No telemetry stack was started or changed.

## Remaining gates

- Groq dispatcher, catalog preflight, crash recovery, and integration of the lease with an authorized run.
- Independent dataset/rubric review, finite free quota and cumulative request/token/cost/time limits, confirmation funding, and pacing.
- Docker/promtool validators, service integration, eventual local canary and rollback, and clean-context review.
- No provider call was made in this phase.
