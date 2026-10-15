# P03 package consumer update

P03 source commit `41af3f7eed8b6ee991e8d9d6d888037c386f7fcc` adds the `flush_telemetry` and `shutdown_telemetry` public functions and releases local wheel `supportops_obs-0.2.0-py3-none-any.whl`.

- SHA-256: `531520844aa94ddbac121aec907533fe565ffceeff3e065d9f62eb9f87119257`
- Build: `uv build --wheel --offline --out-dir artifacts/packages` (exit 0).
- Consumer smoke: installed the wheel into an isolated target and imported `supportops_obs`; version was `0.2.0` and both lifecycle functions were present (exit 0).
- P05 must update its pinned local P03 wheel, record this exact source commit and hash, then run its package-consumer contract checks. No package was published.
