# P03 Git setup audit

Date: 2026-10-15

All commands ran in `C:\estudo\Golpe\lab\projects\p03`.

| Check | Command | Exit | Output |
|---|---|---:|---|
| Repository root | `git rev-parse --show-toplevel` | 0 | `C:/estudo/Golpe/lab/projects/p03` (exact project root) |
| Branch | `git branch --show-current` | 0 | `main` |
| Initial commit | `git log -1 --format=%H` | 0 | `578ec23c795f8b5673036f2d118dc70f59d273b4` |
| Hook configuration | `git config --local core.hooksPath` | 0 | `.githooks` |
| Invalid message | `git hook run commit-msg -- artifacts/evidence/commit-invalid.txt` | 1 | `Invalid commit. Expected type(scope): imperative English description` |
| Valid message | `git hook run commit-msg -- artifacts/evidence/commit-valid.txt` | 0 | no output |
| Ignored sensitive/environment/cache paths | `git check-ignore -v .env .venv/pyvenv.cfg __pycache__/x.pyc .pytest_cache/state .ruff_cache/state secret.pem private.key` | 0 | `.env`, `.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `*.pem`, and `*.key` patterns matched |

The first hook-path inspection found the hook under `.githooks` but `core.hooksPath` was unset. Set only the repository-local value to `.githooks`; global Git identity/configuration was not changed. Direct hook invocation confirmed invalid rejection and valid acceptance. Initial commit is present and locally verifiable.

Commands and exit codes above were observed in the terminal. Captured test message inputs are `commit-invalid.txt` and `commit-valid.txt` in this directory.
