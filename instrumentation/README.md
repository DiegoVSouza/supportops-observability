# Instrumentation package map

The canonical Python implementation is `supportops_obs/instrumentation.py`, installed as the `supportops_obs` package. This folder documents the P03 deliverable path without duplicating the API source.

The package provides `setup_telemetry`, `traced_agent`, `traced_tool`, `traced_operation`, `record_llm_call`, and trace-correlated stdlib logging. Traces use OpenTelemetry API/SDK stable interfaces; exporter wiring is optional through the OTLP endpoint. Content capture is disabled by default.
