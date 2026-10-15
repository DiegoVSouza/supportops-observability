from prometheus_client import generate_latest

import supportops_obs.instrumentation as inst
from demo.integrated_trace import run_integrated_trace


def test_deterministic_synthetic_api_queue_worker_agent_llm_tool_database_trace():
    retries_before = inst.tool_retries_by_type.labels(tool="ticket.lookup", task_type="billing")._value.get()
    evidence = run_integrated_trace()
    spans = evidence["spans"]
    names = [span["name"] for span in spans]
    assert names == [
        "http.api.request",
        "queue.ticket.publish",
        "worker.ticket.consume",
        "agent.supportops.triage",
        "llm.inference",
        "tool.ticket.lookup",
        "database.ticket.read",
        "database.ticket.read",
    ]
    assert {span["trace_id"] for span in spans} == {"00000000000000000000000000000042"}
    assert all(span["synthetic"] is True for span in spans)
    by_name = {span["name"]: span for span in spans}
    assert by_name["queue.ticket.publish"]["parent_span_id"] == by_name["http.api.request"]["span_id"]
    assert by_name["worker.ticket.consume"]["parent_span_id"] == by_name["queue.ticket.publish"]["span_id"]
    assert by_name["agent.supportops.triage"]["parent_span_id"] == by_name["worker.ticket.consume"]["span_id"]
    assert by_name["tool.ticket.lookup"]["parent_span_id"] == by_name["agent.supportops.triage"]["span_id"]
    database_spans = [span for span in spans if span["name"] == "database.ticket.read"]
    assert [span["status"] for span in database_spans] == ["ERROR", "UNSET"]
    assert all(span["parent_span_id"] == by_name["tool.ticket.lookup"]["span_id"] for span in database_spans)
    assert inst.tool_retries_by_type.labels(tool="ticket.lookup", task_type="billing")._value.get() == retries_before + 1
    assert "synthetic" in evidence["classification"]


def test_task_metrics_use_bounded_task_type_and_per_task_cost_histogram():
    success_before = inst.task_type_success.labels(task_type="billing", outcome="success")._value.get()
    error_before = inst.task_type_success.labels(task_type="billing", outcome="error")._value.get()
    cost_before = inst.task_cost.labels(task_type="billing")._sum.get()
    retry_before = inst.tool_retries_by_type.labels(tool="ticket.lookup", task_type="billing")._value.get()

    inst.record_agent_execution(task_type="billing", steps=3, success=True, cost_usd=0.02)
    inst.record_agent_execution(task_type="billing", steps=1, success=False, cost_usd=0.01)
    inst.record_tool_retry("ticket.lookup", task_type="billing")

    assert inst.task_type_success.labels(task_type="billing", outcome="success")._value.get() == success_before + 1
    assert inst.task_type_success.labels(task_type="billing", outcome="error")._value.get() == error_before + 1
    assert abs(inst.task_cost.labels(task_type="billing")._sum.get() - (cost_before + 0.03)) < 1e-9
    assert inst.tool_retries_by_type.labels(tool="ticket.lookup", task_type="billing")._value.get() == retry_before + 1
    payload = generate_latest(inst.metrics_registry()).decode()
    assert "supportops_task_cost_usd" in payload
    assert 'supportops_tasks_by_type_total{outcome="success",task_type="billing"}' in payload
