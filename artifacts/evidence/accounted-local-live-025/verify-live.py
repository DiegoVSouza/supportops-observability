"""Verify the one existing live receipt/trace using read-only queries."""
import json
import sqlite3
import sys
import time
from contextlib import closing
from pathlib import Path

root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(root))
from scripts.check_services import fetch

out = Path(__file__).resolve().parent
result = json.loads((out / "live-result.json").read_text())
assert result["status"] == "ok" and result["provenance"] == "live"
assert result["telemetry_flushed"] is True
for filename, table in (("operations.sqlite", "attempts"), ("provider-usage.sqlite", "usage_events")):
    path = root / "artifacts/evals/live" / filename
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as db:
        db.row_factory = sqlite3.Row
        rows = [dict(row) for row in db.execute("SELECT * FROM " + table)]
    if table == "attempts":
        assert len(rows) == 1 and rows[0]["status"] == "ok"
        assert rows[0]["receipt"] == result["receipt"]
        assert rows[0]["input_tokens"] == result["input_tokens"]
        assert rows[0]["output_tokens"] == result["output_tokens"]
    else:
        assert len(rows) == 2
        completed = [row for row in rows if row["event"] == "completed"]
        assert len(completed) == 1 and completed[0]["status"] == "ok"
        assert completed[0]["attempt_id"] == result["receipt"]
        assert completed[0]["actual_input"] == result["input_tokens"]
        assert completed[0]["actual_output"] == result["output_tokens"]
time.sleep(0.5)
data = None
for index in range(5):
    data = fetch("http://127.0.0.1:24686/api/traces/" + result["trace_id"])
    if data.get("data"):
        break
    time.sleep(0.5)
spans = data["data"][0]["spans"]
by_name = {span["operationName"]: span for span in spans}
parent, child = by_name["agent.accounted-operation"], by_name["llm.inference"]
assert child["references"][0]["spanID"] == parent["spanID"]
assert child["traceID"] == parent["traceID"] == result["trace_id"]
allowed = {"supportops.operation.kind", "supportops.operation.name", "supportops.llm.provider", "supportops.llm.model",
           "supportops.llm.input_tokens", "supportops.llm.output_tokens", "supportops.llm.cost_usd",
           "supportops.llm.latency_seconds", "supportops.llm.success"}
for span in spans:
    assert not span.get("logs")
    for tag in span["tags"]:
        if tag["key"].startswith("supportops."):
            assert tag["key"] in allowed
        assert "content" not in tag["key"] and "description" not in tag["key"]
        assert result["receipt"] not in str(tag["value"])
tags = {tag["key"]: tag["value"] for tag in child["tags"]}
assert tags["supportops.llm.input_tokens"] == result["input_tokens"]
assert tags["supportops.llm.output_tokens"] == result["output_tokens"]
report = {"status": "PASS", "receipt_matches": True, "correlated_spans": 2,
          "content_exported": False, "provider_calls": 1, "remaining_operating_calls": 3,
          "input_tokens": result["input_tokens"], "output_tokens": result["output_tokens"],
          "trace_id": result["trace_id"], "actual_billed_usd": None}
(out / "reconciliation.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report))
