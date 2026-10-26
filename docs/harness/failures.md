# Failures

Record recurring builder or product failures here before fixing them.

## 2026-10-26 — Live acceptance finding

The first Docker gate exceeded its cold-start synthetic-alert wait. All four alerts later fired; increasing the configurable wait to 600 seconds preserved thresholds. The subsequent full gate passed with no incomplete checks. A real Groq completion (103 input / 64 output tokens) exported parent and inference spans over OTLP. Jaeger independently confirmed provider, model, usage and absent content. Failed attempt artifacts remain alongside the correction.
