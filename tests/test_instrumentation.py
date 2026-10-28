import logging
import asyncio
from prometheus_client import generate_latest
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

import supportops_obs.instrumentation as inst
from supportops_obs import LLMResponse, record_agent_execution, record_llm_call, record_tool_retry, traced_agent, traced_operation, traced_tool


def memory_tracer(monkeypatch):
    exporter = InMemorySpanExporter()
    provider = TracerProvider(resource=Resource.create({"service.name": "tests"}))
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    monkeypatch.setattr(inst, "_tracer", provider.get_tracer("tests"))
    return exporter


def test_nested_agent_tool_spans_and_error(monkeypatch):
    exporter = memory_tracer(monkeypatch)

    @traced_tool("lookup")
    def lookup():
        return "ok"

    @traced_agent("triage")
    def agent():
        return lookup()

    assert agent() == "ok"
    spans = exporter.get_finished_spans()
    by_name = {span.name: span for span in spans}
    assert set(by_name) == {"agent.triage", "tool.lookup"}
    assert by_name["tool.lookup"].parent.span_id == by_name["agent.triage"].context.span_id
    assert by_name["tool.lookup"].context.trace_id == by_name["agent.triage"].context.trace_id
    assert by_name["tool.lookup"].attributes["supportops.operation.kind"] == "tool"

    @traced_tool("broken")
    def broken():
        raise RuntimeError("expected")

    import pytest
    with pytest.raises(RuntimeError):
        broken()
    assert exporter.get_finished_spans()[-1].status.status_code.name == "ERROR"


def test_sync_failure_span_omits_exception_message_and_traceback(monkeypatch):
    exporter = memory_tracer(monkeypatch)
    secret = "private prompt and ticket body"

    @traced_tool("private-failure")
    def fails():
        raise ValueError(secret)

    import pytest
    with pytest.raises(ValueError, match="private prompt"):
        fails()
    span = exporter.get_finished_spans()[0]
    assert span.status.status_code.name == "ERROR"
    assert span.attributes["supportops.error.category"] == "validation"
    assert secret not in repr(span.attributes)
    assert secret not in repr(span.events)
    assert span.events == ()


def test_async_failure_span_omits_exception_message_and_traceback(monkeypatch):
    exporter = memory_tracer(monkeypatch)
    secret = "private async prompt"

    @traced_tool("private-async-failure")
    async def fails():
        raise RuntimeError(secret)

    import pytest
    with pytest.raises(RuntimeError, match="private async prompt"):
        asyncio.run(fails())
    span = exporter.get_finished_spans()[0]
    assert span.status.status_code.name == "ERROR"
    assert span.attributes["supportops.error.category"] == "application"
    assert secret not in repr(span.attributes)
    assert secret not in repr(span.events)
    assert span.events == ()


def test_sync_failure_span_status_description_omits_exception_message(monkeypatch):
    exporter = memory_tracer(monkeypatch)
    sentinel = "private-status-sentinel-sync"

    @traced_tool("private-status-sync")
    def fails():
        raise RuntimeError(sentinel)

    import pytest
    with pytest.raises(RuntimeError, match=sentinel):
        fails()
    span = exporter.get_finished_spans()[0]
    assert span.status.status_code.name == "ERROR"
    assert span.status.description is None
    assert sentinel not in repr(span)


def test_async_failure_span_status_description_omits_exception_message(monkeypatch):
    exporter = memory_tracer(monkeypatch)
    sentinel = "private-status-sentinel-async"

    @traced_tool("private-status-async")
    async def fails():
        raise RuntimeError(sentinel)

    import pytest
    with pytest.raises(RuntimeError, match=sentinel):
        asyncio.run(fails())
    span = exporter.get_finished_spans()[0]
    assert span.status.status_code.name == "ERROR"
    assert span.status.description is None
    assert sentinel not in repr(span)


def test_operation_metrics_work_with_non_recording_span(monkeypatch):
    from opentelemetry import trace

    monkeypatch.setattr(inst, "_tracer", trace.NoOpTracerProvider().get_tracer("noop-test"))

    @traced_operation("database", "tickets.add")
    def add_ticket():
        return "created"

    before = inst.operation_calls.labels(kind="database", outcome="success")._value.get()
    assert add_ticket() == "created"
    assert inst.operation_calls.labels(kind="database", outcome="success")._value.get() == before + 1


def test_agent_tool_database_llm_tree_and_log_correlation(monkeypatch):
    exporter = memory_tracer(monkeypatch)
    inst._install_log_correlation()
    captured = {}

    @traced_operation("database", "tickets.query")
    def db():
        captured["db_trace_id"] = logging.getLogger("supportops.demo.db").makeRecord("supportops.demo.db", logging.INFO, "", 1, "query", (), None).trace_id
        return {"status": "open"}

    @traced_tool("tickets.lookup")
    def tool():
        return db()

    @traced_agent("support.triage")
    def agent():
        result = tool()
        record_llm_call(LLMResponse("fake", "fixture-model", 2, 1, 0, 0.01))
        return result

    assert agent() == {"status": "open"}
    spans = {span.name: span for span in exporter.get_finished_spans()}
    root = spans["agent.support.triage"]
    assert spans["tool.tickets.lookup"].parent.span_id == root.context.span_id
    assert spans["database.tickets.query"].parent.span_id == spans["tool.tickets.lookup"].context.span_id
    assert spans["llm.inference"].parent.span_id == root.context.span_id
    assert len({span.context.trace_id for span in spans.values()}) == 1
    assert captured["db_trace_id"] == f"{root.context.trace_id:032x}"


def test_log_filter_correlates_trace_and_span(monkeypatch):
    exporter = memory_tracer(monkeypatch)
    inst._install_log_correlation()
    logger = logging.getLogger("supportops.test.child")
    captured = {}
    with inst._tracer.start_as_current_span("parent"):
        record = logger.makeRecord(logger.name, logging.INFO, "", 1, "hello", (), None)
        captured.update(trace_id=record.trace_id, span_id=record.span_id)
    span = exporter.get_finished_spans()[0]
    assert captured == {"trace_id": f"{span.context.trace_id:032x}", "span_id": f"{span.context.span_id:016x}"}


def test_llm_metrics_and_content_privacy(monkeypatch):
    exporter = memory_tracer(monkeypatch)
    monkeypatch.setattr(inst, "_capture_content", False)
    calls_before = inst.llm_calls.labels(provider="fake", outcome="success")._value.get()
    tokens_before = inst.llm_tokens.labels(kind="output")._value.get()
    record_llm_call(LLMResponse("fake", "fixture-model", 4, 6, 0.02, 0.4, content="PRIVATE PROMPT"))
    span = exporter.get_finished_spans()[0]
    assert "supportops.llm.content" not in span.attributes
    assert span.attributes["supportops.llm.input_tokens"] == 4
    payload = generate_latest(inst.metrics_registry()).decode()
    assert inst.llm_calls.labels(provider="fake", outcome="success")._value.get() == calls_before + 1
    assert inst.llm_tokens.labels(kind="output")._value.get() == tokens_before + 6
    assert 'supportops_llm_calls_total{outcome="success",provider="fake"}' in payload
    assert "supportops_llm_cost_usd_total" in payload


def test_content_capture_requires_opt_in(monkeypatch):
    exporter = memory_tracer(monkeypatch)
    monkeypatch.setattr(inst, "_capture_content", True)
    record_llm_call(LLMResponse("fake", "fixture", 1, 1, 0, 0, content="explicit test payload"))
    assert exporter.get_finished_spans()[0].attributes["supportops.llm.content"] == "explicit test payload"


def test_invalid_llm_measurements_fail_closed():
    import pytest
    with pytest.raises(ValueError):
        record_llm_call(LLMResponse("fake", "fixture", -1, 0, 0, 0))
    with pytest.raises(ValueError):
        record_llm_call(LLMResponse("fake", "fixture", 0, 0, -0.01, 0))
    with pytest.raises(ValueError):
        record_llm_call(LLMResponse("fake", "fixture", 1, 0, float("nan"), 0))
    with pytest.raises(ValueError):
        record_llm_call(LLMResponse("fake", "fixture", 1.5, 0, 0, 0))


def test_setup_rejects_blank_service_name():
    import pytest
    with pytest.raises(ValueError):
        inst.setup_telemetry("  ", otlp_endpoint=None)


def test_setup_does_not_mutate_active_capture_configuration(monkeypatch):
    monkeypatch.setattr(inst, "_provider", object())
    monkeypatch.setattr(inst, "_capture_content", False)
    inst.setup_telemetry("later-service", otlp_endpoint="http://ignored", capture_content=True)
    assert inst._capture_content is False


def test_provider_flush_and_shutdown_are_exposed(monkeypatch):
    class Provider:
        def __init__(self):
            self.flushed = []
            self.shutdowns = []

        def force_flush(self, timeout_millis=30000):
            self.flushed.append(timeout_millis)
            return True

        def shutdown(self):
            self.shutdowns.append(True)

    provider = Provider()
    monkeypatch.setattr(inst, "_provider", provider)
    monkeypatch.setattr(inst, "_provider_shutdown", False)
    monkeypatch.setattr(inst, "_shutdown_result", None)
    assert inst.flush_telemetry(timeout_millis=1234) is True
    assert inst.shutdown_telemetry() is True
    assert inst.shutdown_telemetry() is True
    assert provider.flushed == [1234]
    assert provider.shutdowns == [True]


def test_flush_and_shutdown_errors_are_counted_and_do_not_escape(monkeypatch):
    class BrokenProvider:
        def __init__(self):
            self.shutdowns = 0

        def force_flush(self, timeout_millis=30000):
            raise RuntimeError("private exporter response")

        def shutdown(self):
            self.shutdowns += 1
            raise RuntimeError("private shutdown detail")

    provider = BrokenProvider()
    monkeypatch.setattr(inst, "_provider", provider)
    monkeypatch.setattr(inst, "_provider_shutdown", False)
    monkeypatch.setattr(inst, "_shutdown_result", None)
    flush_before = inst.telemetry_export_failures.labels(operation="flush")._value.get()
    shutdown_before = inst.telemetry_export_failures.labels(operation="shutdown")._value.get()
    assert inst.flush_telemetry(timeout_millis=10) is False
    assert inst.telemetry_export_failures.labels(operation="flush")._value.get() == flush_before + 1
    assert inst.shutdown_telemetry() is False
    assert inst.shutdown_telemetry() is False
    assert provider.shutdowns == 1
    assert inst.telemetry_export_failures.labels(operation="shutdown")._value.get() == shutdown_before + 1


def test_exporter_setup_failure_is_reported_and_does_not_install_provider(monkeypatch):
    class Provider:
        def __init__(self, **kwargs):
            self.processors = []

        def add_span_processor(self, processor):
            self.processors.append(processor)

    def broken_exporter(**kwargs):
        raise RuntimeError("private endpoint detail")

    monkeypatch.setattr(inst, "_provider", None)
    monkeypatch.setattr(inst, "_provider_shutdown", False)
    monkeypatch.setattr(inst, "TracerProvider", Provider)
    monkeypatch.setattr(inst, "OTLPSpanExporter", broken_exporter)
    installed = []
    monkeypatch.setattr(inst.trace, "set_tracer_provider", lambda provider: installed.append(provider))
    before = inst.telemetry_export_failures.labels(operation="setup")._value.get()
    assert inst.setup_telemetry("setup-failure-test", otlp_endpoint="http://127.0.0.1:4317") is False
    assert installed == []
    assert inst._provider is None
    assert inst.telemetry_export_failures.labels(operation="setup")._value.get() == before + 1


def test_async_tool_span_and_exception_status(monkeypatch):
    exporter = memory_tracer(monkeypatch)

    @traced_tool("async.lookup")
    async def lookup():
        return "ok"

    assert asyncio.run(lookup()) == "ok"
    assert exporter.get_finished_spans()[0].name == "tool.async.lookup"


def test_failed_llm_call_records_error_outcome(monkeypatch):
    memory_tracer(monkeypatch)
    record_llm_call(LLMResponse("fake", "fixture", 0, 0, 0, 0, success=False))
    assert 'outcome="error"' in generate_latest(inst.metrics_registry()).decode()


def test_task_steps_success_and_tool_retries_are_recorded():
    task_before = inst.task_success.labels(outcome="success")._value.get()
    retry_before = inst.tool_retries.labels(tool="ticket.lookup")._value.get()
    step_sum_before = inst.task_steps.labels(outcome="success")._sum.get()
    record_agent_execution(steps=3, success=True)
    record_tool_retry("ticket.lookup")
    assert inst.task_success.labels(outcome="success")._value.get() == task_before + 1
    assert inst.task_steps.labels(outcome="success")._sum.get() == step_sum_before + 3
    assert inst.tool_retries.labels(tool="ticket.lookup")._value.get() == retry_before + 1
