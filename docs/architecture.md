# Architecture

`supportops_obs` exposes a small Python instrumentation API. OpenTelemetry API/SDK create nested spans, while a package logger emits trace and span identifiers for correlation. Prometheus instruments counters and histograms. A deterministic loop detector consumes caller-provided step records and is independent of any LLM runtime.

The demo uses a local runner contract double. It does not import sibling project source. Production integration with P01 requires a versioned package installation and recorded provenance. Content capture is disabled by default; logs and spans avoid prompt and argument values by default.

The optional local observability stack contains the Collector, Jaeger, Prometheus, and Grafana. Dashboards and alert rules are provisioned as project artifacts.

Telemetry decorators record a fixed error category and generic span error status without exception events, status descriptions, messages, or tracebacks. The OpenTelemetry context manager's automatic status mutation is disabled so the exception message cannot become the ERROR description; the original exception still propagates to the caller. Setup, flush, and shutdown return boolean status and increment the fixed-cardinality telemetry export failure counter on failure. This does not establish delivery of every batch or production exporter reliability.

The latest isolated fake service run on the status-privacy candidate completed its three task submissions but did not complete the Jaeger stage assertions because one read ended in `RemoteDisconnected`. Subsequent diagnostic GETs succeeded; that does not convert the failed acceptance gate to PASS. See phase 018 for the exact scope and cleanup.

The service checker retries only transport failures on read-only observability GETs, at most three requests with short fixed delays; HTTP errors and model/application actions are not retried. Phase 019's service gate still exhausted this bound, with the endpoint unidentified, so current-candidate service acceptance remains INCOMPLETE.
