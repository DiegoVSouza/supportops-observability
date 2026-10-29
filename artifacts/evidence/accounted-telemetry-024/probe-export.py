"""Export fixture-accounted telemetry to the phase-owned local services."""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from opentelemetry import trace
from supportops_obs import setup_telemetry, flush_telemetry, shutdown_telemetry
from supportops_obs.accounted import MODEL, run
from scripts.check_services import fetch

out = Path(__file__).resolve().parent
assert setup_telemetry("p03-accounted-fixture-024", otlp_endpoint="http://127.0.0.1:24317", capture_content=True)


class Session:
    provenance = "fixture"
    trace_id = None

    def preview(self, envelope):
        pass

    def complete(self, envelope):
        self.trace_id = format(trace.get_current_span().get_span_context().trace_id, "032x")
        return {"status": "ok", "model": MODEL, "attempt_id": "c" * 32,
                "usage": {"input_tokens": 101, "output_tokens": 19},
                "content": "SYNTHETIC_PRIVATE_SENTINEL_024"}


session = Session()
path = out / "fixture-operation.sqlite"
assert not path.exists(), "Do not replay the service probe"
result = run(path, "fixture-export-024", session)
assert flush_telemetry(timeout_millis=10000)
time.sleep(0.5)
try:
    data = None
    for index in range(5):
        data = fetch("http://127.0.0.1:24686/api/traces/" + session.trace_id)
        if data.get("data"):
            break
        time.sleep(0.5)
    spans = data["data"][0]["spans"]
    by_name = {span["operationName"]: span for span in spans}
    parent, child = by_name["agent.accounted-operation"], by_name["llm.inference"]
    assert child["references"][0]["spanID"] == parent["spanID"]
    assert child["traceID"] == parent["traceID"]
    assert "SYNTHETIC_PRIVATE_SENTINEL_024" not in json.dumps(data)
    tags = {row["key"]: row["value"] for row in child["tags"]}
    assert tags["supportops.llm.input_tokens"] == 101
    assert tags["supportops.llm.output_tokens"] == 19
    report = {"status": "PASS", "provenance": "fixture", "trace_id": session.trace_id,
              "correlated_spans": 2, "content_exported": False, "provider_calls": 0,
              "fixture_input_tokens": 101, "fixture_output_tokens": 19}
    (out / "accounted-export.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(json.dumps(report))
finally:
    assert shutdown_telemetry()
