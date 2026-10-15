"""Stable synthetic API-to-database trace using local functions and an in-memory exporter."""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from opentelemetry.sdk.trace.id_generator import IdGenerator

import supportops_obs.instrumentation as inst
from supportops_obs import LLMResponse, record_agent_execution, record_llm_call, record_tool_retry, traced_agent, traced_operation, traced_tool


class StableIds(IdGenerator):
    def __init__(self) -> None:
        self.span_id = 100

    def generate_trace_id(self) -> int:
        return 0x42

    def generate_span_id(self) -> int:
        self.span_id += 1
        return self.span_id


@contextmanager
def local_span(name: str, kind: str) -> Iterator[None]:
    with inst._tracer.start_as_current_span(name) as span:
        span.set_attribute("supportops.operation.kind", kind)
        span.set_attribute("supportops.demo.synthetic", True)
        yield


def run_integrated_trace() -> dict[str, Any]:
    exporter = InMemorySpanExporter()
    provider = TracerProvider(
        resource=Resource.create({"service.name": "p03-synthetic-trace", "supportops.evidence.synthetic": True}),
        id_generator=StableIds(),
    )
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    original_tracer = inst._tracer
    inst._tracer = provider.get_tracer("supportops_obs.synthetic")
    database_attempts = 0

    @traced_operation("database", "ticket.read")
    def read_ticket() -> dict[str, str]:
        nonlocal database_attempts
        database_attempts += 1
        trace.get_current_span().set_attribute("supportops.demo.synthetic", True)
        if database_attempts == 1:
            raise TimeoutError("synthetic transient database failure")
        return {"ticket_id": "T-SYNTHETIC", "status": "open"}

    @traced_tool("ticket.lookup")
    def lookup_ticket() -> dict[str, str]:
        trace.get_current_span().set_attribute("supportops.demo.synthetic", True)
        try:
            return read_ticket()
        except TimeoutError:
            record_tool_retry("ticket.lookup", task_type="billing")
            return read_ticket()

    @traced_agent("supportops.triage")
    def run_agent(ticket_id: str) -> dict[str, str]:
        trace.get_current_span().set_attribute("supportops.demo.synthetic", True)
        record_llm_call(LLMResponse("fake", "fixture-model", 12, 5, 0.001, 0.002))
        return {**lookup_ticket(), "classification": "billing_question", "requested_ticket": ticket_id}

    @traced_operation("http", "api.request")
    def api_request(ticket_id: str) -> dict[str, str]:
        trace.get_current_span().set_attribute("supportops.demo.synthetic", True)
        with local_span("queue.ticket.publish", "queue"):
            with local_span("worker.ticket.consume", "worker"):
                return run_agent(ticket_id)

    try:
        result = api_request("T-SYNTHETIC")
        record_agent_execution(task_type="billing", steps=4, success=True, cost_usd=0.001)
        spans = sorted(exporter.get_finished_spans(), key=lambda item: item.start_time or 0)
        return {
            "classification": "synthetic in-process functions; no network API, broker, worker service, live LLM, or database",
            "result": result,
            "spans": [
                {
                    "name": span.name,
                    "span_id": f"{span.context.span_id:016x}",
                    "parent_span_id": f"{span.parent.span_id:016x}" if span.parent else None,
                    "trace_id": f"{span.context.trace_id:032x}",
                    "synthetic": span.resource.attributes.get("supportops.evidence.synthetic") is True
                    or span.attributes.get("supportops.demo.synthetic") is True,
                    "status": span.status.status_code.name,
                }
                for span in spans
            ],
        }
    finally:
        inst._tracer = original_tracer
        provider.shutdown()


def main() -> int:
    evidence = run_integrated_trace()
    expected = [
        "http.api.request", "queue.ticket.publish", "worker.ticket.consume",
        "agent.supportops.triage", "llm.inference", "tool.ticket.lookup",
        "database.ticket.read", "database.ticket.read",
    ]
    if [span["name"] for span in evidence["spans"]] != expected:
        raise SystemExit("synthetic trace topology mismatch")
    if {span["trace_id"] for span in evidence["spans"]} != {"00000000000000000000000000000042"}:
        raise SystemExit("synthetic trace correlation mismatch")
    if not all(span["synthetic"] for span in evidence["spans"]):
        raise SystemExit("synthetic trace labeling missing")
    path = Path("artifacts/evidence/integrated-trace-synthetic.json")
    path.write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"synthetic_trace=PASS; spans={len(evidence['spans'])}; trace_id=00000000000000000000000000000042; output={path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
