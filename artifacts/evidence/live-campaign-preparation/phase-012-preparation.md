# P03 Phase 012 — campaign preparation evidence

This preparation used offline data and in-memory simulations only. No Groq call, provider catalog lookup, credential read, network access, Docker/service mutation, prompt export, or production result is claimed. Paid authorization remains USD 0.

| Command | Exit | Result |
|---|---:|---|
| `uv run --locked python scripts/run_live_campaign.py --stage pilot --dry-run` | 0 | 6 scenarios × 1 trial = 6 calls. |
| `uv run --locked python scripts/run_live_campaign.py --stage development --dry-run` | 0 | 9 scenarios × 3 trials = 27 calls. |
| `uv run --locked python scripts/run_live_campaign.py --stage holdout --dry-run` | 0 | 21 scenarios × 3 trials = 63 calls. |
| `uv run --locked python -m unittest discover -s tests -p test_live_campaign_preparation.py -v` | 0 | 7 focused campaign tests passed. |
| `uv run --locked python scripts/check_fast.py` | 0 | `check-fast: OK`. |
| `uv run --locked python -m pytest tests` | 0 | 39 offline unit tests passed. |

Dataset SHA-256: `e9b9ac4d1b1c3c85ffd48d3b30b932734d47ababa3f777b76bb5c6c538e68633`. It contains 30 synthetic scenarios, split 9/21 across development and fixed holdout. Six families contain five each; language is `NOT_APPLICABLE`.

Planned reservation maxima, not approval or consumption: pilot 6 calls; primary campaign 90 calls / 368,640 input / 46,080 output tokens; fresh confirmation 20 scenarios × 3 trials = 60 calls / 245,760 input / 30,720 output tokens; additive pilot + primary + confirmation = 156 calls / 638,976 input / 79,872 output tokens. Each scenario trial is capped at one provider request, 4,096 input tokens, 512 output tokens, and 45 seconds. Paid budget remains USD 0. Quota, cumulative caps, confirmation funding, reviewer approval, pacing, wall-clock ceiling, authenticated model preflight, clean-context verification, and durable lease/ledger remain pending.

Dry-run reports and command outputs are stored beside this report. This is preparation evidence, not live telemetry quality evidence.
