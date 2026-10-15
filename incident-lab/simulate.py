"""Generate deterministic synthetic spans for the three incident runbooks."""

from __future__ import annotations

import json
from pathlib import Path

from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

import supportops_obs.instrumentation as instrumentation
from supportops_obs import LLMResponse, LoopDetector, StepRecord, record_llm_call

ROOT = Path(__file__).resolve().parents[1]


def simulate() -> dict[str, object]:
    exporter = InMemorySpanExporter()
    provider = TracerProvider(resource=Resource.create({"service.name": "supportops-incident-lab"}))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    instrumentation._tracer = provider.get_tracer("incident-lab")
    instrumentation._capture_content = False
    results: dict[str, object] = {"source": "synthetic local test run; not a production incident", "scenarios": {}}
    tracer = instrumentation._tracer

    with tracer.start_as_current_span("agent.slow_tool") as agent:
        with tracer.start_as_current_span("tool.lookup") as tool:
            tool.set_attribute("supportops.simulated.duration_ms", 8200)
            tool.set_attribute("supportops.simulated.cause", "slow tool dependency")
    results["scenarios"]["tool_slow"] = {"expected_cause": "tool.lookup dominates latency", "agent_span": agent.name, "tool_span": tool.name}

    detector = LoopDetector(repeat_threshold=3, cycle_threshold=3)
    with tracer.start_as_current_span("agent.loop") as agent:
        for index in range(6):
            with tracer.start_as_current_span("tool.search") as tool:
                tool.set_attribute("supportops.simulated.step", index + 1)
            signal = detector.observe(StepRecord(tool="search", arguments={"ticket": "SYNTHETIC"}, state=("plan", "act")[index % 2]))
        agent.set_attribute("supportops.loop.detected", signal.detected)
        agent.set_attribute("supportops.loop.reason", signal.reason or "none")
    results["scenarios"]["agent_loop"] = {"detected": signal.detected, "reason": signal.reason}

    with tracer.start_as_current_span("agent.cost_spike"):
        record_llm_call(LLMResponse("fake", "synthetic-model", 100000, 20000, 8.75, 2.1))
    results["scenarios"]["cost_spike"] = {"cost_usd": 8.75, "input_tokens": 100000, "output_tokens": 20000, "synthetic": True}

    results["spans"] = [
        {"name": span.name, "trace_id": f"{span.context.trace_id:032x}", "parent_span_id": f"{span.parent.span_id:016x}" if span.parent else None, "attributes": dict(span.attributes)}
        for span in exporter.get_finished_spans()
    ]
    return results


def main() -> None:
    output = simulate()
    target = ROOT / "artifacts" / "evidence" / "incident-simulation.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    scenarios = output["scenarios"]
    if not scenarios["agent_loop"]["detected"] or scenarios["agent_loop"]["reason"] != "repeated_tool_arguments":
        raise SystemExit("synthetic loop simulation did not detect repeated calls")
    print(f"simulated_incidents=3 spans={len(output['spans'])} output={target.relative_to(ROOT)} real_incident_traces=PENDING")


if __name__ == "__main__":
    main()
