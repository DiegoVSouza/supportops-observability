# Architecture

`supportops_obs` exposes a small Python instrumentation API. OpenTelemetry API/SDK create nested spans, while a package logger emits trace and span identifiers for correlation. Prometheus instruments counters and histograms. A deterministic loop detector consumes caller-provided step records and is independent of any LLM runtime.

The demo uses a local runner contract double. It does not import sibling project source. Production integration with P01 requires a versioned package installation and recorded provenance. Content capture is disabled by default; logs and spans avoid prompt and argument values by default.

The optional local observability stack contains the Collector, Jaeger, Prometheus, and Grafana. Dashboards and alert rules are provisioned as project artifacts.

Telemetry decorators record a fixed error category and span error status without exception events, messages, or tracebacks. Setup, flush, and shutdown return boolean status and increment the fixed-cardinality telemetry export failure counter on failure. This does not establish delivery of every batch or production exporter reliability.
