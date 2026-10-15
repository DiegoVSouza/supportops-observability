"""Local P01 runner contract double; no sibling project imports or model calls."""

import argparse
import os
import time

from prometheus_client import start_http_server

from supportops_obs import LLMResponse, LoopDetector, StepRecord, metrics_registry, record_agent_execution, record_llm_call, setup_telemetry, traced_agent, traced_tool


@traced_tool("ticket.lookup")
def lookup_ticket(ticket_id: str) -> dict[str, str]:
    return {"ticket_id": ticket_id, "status": "open"}


@traced_agent("supportops.triage")
def run_demo(ticket_id: str) -> dict[str, str]:
    ticket = lookup_ticket(ticket_id)
    record_llm_call(LLMResponse("fake", "fixture-model", 23, 8, 0.0, 0.001, content="redacted in telemetry"))
    return {**ticket, "classification": "billing_question"}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="run a single smoke and exit")
    args = parser.parse_args()
    llm_mode = os.getenv("LLM_MODE", "fake")
    if llm_mode != "fake":
        raise SystemExit("demo runner double supports only LLM_MODE=fake")
    setup_telemetry("p03-demo", otlp_endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"), capture_content=False)
    detector = LoopDetector(max_steps=10)
    detector.observe(StepRecord(tool="ticket.lookup", arguments={"ticket_id": "T-DEMO"}, state="start"))
    result = run_demo("T-DEMO")
    record_agent_execution(steps=2, success=True)
    server, thread = start_http_server(8000, addr="0.0.0.0", registry=metrics_registry())
    print(f"LLM_MODE=fake; metrics=http://localhost:8000; P01 integration=INCOMPLETE (local contract double); result={result}")
    if not args.once:
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            pass
    server.shutdown()
    server.server_close()
    thread.join(timeout=1)


if __name__ == "__main__":
    main()
