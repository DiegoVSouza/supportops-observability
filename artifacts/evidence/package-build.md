# P03 local package artifact

| Item | Value |
|---|---|
| Build command | `uv build --out-dir artifacts/packages` |
| Build exit code | 0 |
| Build output | `Successfully built artifacts\packages\supportops_obs-0.1.0.tar.gz` and `Successfully built artifacts\packages\supportops_obs-0.1.0-py3-none-any.whl` |
| Package version | `supportops-obs==0.1.0` |
| Source commit | `7d78bf63f42b03c510792773ad2c9915015120e9` |
| Wheel SHA-256 | `e4e80cd664c97cf38b8fbe5557f10d4c8d247af275412569fb6a1bcbc0f11575` |
| Publication | Local project artifact only; not published externally |

| Install command | `uv pip install --target artifacts/packages/.wheel-install --no-deps artifacts/packages/supportops_obs-0.1.0-py3-none-any.whl` |
| Install exit code | 0 |
| Import command | `\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'artifacts/packages/.wheel-install'); import supportops_obs; print(supportops_obs.__file__); print(supportops_obs.LoopDetector.__name__)"` |
| Import exit code/output | 0; loaded from the isolated wheel target and printed `LoopDetector` |

The first import probe used system Python without project dependencies and exited 1 with `ModuleNotFoundError: prometheus_client`. This is expected from the explicit `--no-deps` install target; repeating the import with the project's locked `.venv` succeeded. The isolated install target is ignored and not part of the package artifact.
