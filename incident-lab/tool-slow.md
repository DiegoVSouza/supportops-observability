# Incident: slow tool

1. In Grafana, select the incident time window and inspect the latency panel and agent error/task panels.
2. Open the exemplar trace in Jaeger and find the longest child span under the agent span.
3. Check `tool.lookup` attributes and its child `db.query`; compare duration and status.
4. If tool time dominates and the DB child is short, inspect tool dependency/network timeout logs. Do not infer a DB fault from the parent duration alone.

The committed fixture is synthetic. A real exported trace and screenshot are PENDING.
