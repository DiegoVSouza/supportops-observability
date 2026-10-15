"""Manual instrumentation helpers with safe-by-default content handling."""

from __future__ import annotations

import functools
import inspect
import logging
import time
from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import CollectorRegistry, Counter, Histogram

F = TypeVar("F", bound=Callable[..., Any])
_tracer = trace.get_tracer("supportops_obs")
_provider: TracerProvider | None = None
_capture_content = False
_registry = CollectorRegistry()
llm_calls = Counter("supportops_llm_calls_total", "LLM calls", ["provider", "outcome"], registry=_registry)
llm_tokens = Counter("supportops_llm_tokens_total", "LLM tokens", ["kind"], registry=_registry)
llm_cost = Counter("supportops_llm_cost_usd_total", "LLM cost in USD", registry=_registry)
llm_latency = Histogram("supportops_llm_latency_seconds", "LLM latency in seconds", registry=_registry)
task_steps = Histogram("supportops_agent_steps", "Steps per agent execution", ["outcome"], registry=_registry)
tool_retries = Counter("supportops_tool_retries_total", "Tool retries", ["tool"], registry=_registry)
task_success = Counter("supportops_tasks_total", "Completed agent tasks", ["outcome"], registry=_registry)
loop_signals = Counter("supportops_agent_loop_signals_total", "Detected agent loop signals", ["reason"], registry=_registry)
operation_calls = Counter("supportops_operation_calls_total", "Instrumented operation calls", ["kind", "outcome"], registry=_registry)
operation_latency = Histogram("supportops_operation_latency_seconds", "Agent/tool/database/HTTP operation latency", ["kind", "outcome"], registry=_registry)


@dataclass(frozen=True)
class LLMResponse:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost_usd: float
    latency_seconds: float
    success: bool = True
    content: str | None = None


class TraceContextFilter(logging.Filter):
    """Attach W3C trace identifiers to log records without capturing content."""

    def filter(self, record: logging.LogRecord) -> bool:
        context = trace.get_current_span().get_span_context()
        record.trace_id = f"{context.trace_id:032x}" if context.is_valid else ""
        record.span_id = f"{context.span_id:016x}" if context.is_valid else ""
        return True


def _install_log_correlation() -> None:
    """Enrich every new LogRecord, including records from child loggers."""
    if getattr(logging, "_supportops_trace_factory_installed", False):
        return
    previous_factory = logging.getLogRecordFactory()

    def factory(*args: Any, **kwargs: Any) -> logging.LogRecord:
        record = previous_factory(*args, **kwargs)
        TraceContextFilter().filter(record)
        return record

    logging.setLogRecordFactory(factory)
    setattr(logging, "_supportops_trace_factory_installed", True)


def setup_telemetry(service_name: str, *, otlp_endpoint: str | None, capture_content: bool = False) -> None:
    """Configure the process tracer. Repeated calls are safe and first call wins."""
    global _provider, _capture_content
    if not service_name.strip():
        raise ValueError("service_name must not be blank")
    _capture_content = bool(capture_content)
    if _provider is not None:
        return
    _provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    if otlp_endpoint:
        _provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=otlp_endpoint.startswith("http://"))))
    trace.set_tracer_provider(_provider)
    _install_log_correlation()


def _decorator(kind: str, name: str | None) -> Callable[[F], F]:
    def decorate(fn: F) -> F:
        span_name = name or fn.__qualname__
        if inspect.iscoroutinefunction(fn):
            @functools.wraps(fn)
            async def async_wrapped(*args: Any, **kwargs: Any) -> Any:
                with _tracer.start_as_current_span(f"{kind}.{span_name}") as span:
                    span.set_attribute("supportops.operation.kind", kind)
                    started = time.perf_counter()
                    try:
                        result = await fn(*args, **kwargs)
                        operation_calls.labels(kind=kind, outcome="success").inc()
                        return result
                    except Exception as exc:
                        operation_calls.labels(kind=kind, outcome="error").inc()
                        span.record_exception(exc)
                        span.set_status(trace.Status(trace.StatusCode.ERROR))
                        raise
                    finally:
                        outcome = "error" if span.status.status_code == trace.StatusCode.ERROR else "success"
                        operation_latency.labels(kind=kind, outcome=outcome).observe(time.perf_counter() - started)
            return async_wrapped  # type: ignore[return-value]

        @functools.wraps(fn)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            with _tracer.start_as_current_span(f"{kind}.{span_name}") as span:
                span.set_attribute("supportops.operation.kind", kind)
                started = time.perf_counter()
                try:
                    result = fn(*args, **kwargs)
                    operation_calls.labels(kind=kind, outcome="success").inc()
                    return result
                except Exception as exc:
                    operation_calls.labels(kind=kind, outcome="error").inc()
                    span.record_exception(exc)
                    span.set_status(trace.Status(trace.StatusCode.ERROR))
                    raise
                finally:
                    outcome = "error" if span.status.status_code == trace.StatusCode.ERROR else "success"
                    operation_latency.labels(kind=kind, outcome=outcome).observe(time.perf_counter() - started)
        return wrapped  # type: ignore[return-value]
    return decorate


def traced_agent(name: str | None = None) -> Callable[[F], F]:
    return _decorator("agent", name)


def traced_tool(name: str | None = None) -> Callable[[F], F]:
    return _decorator("tool", name)


def traced_operation(kind: str, name: str | None = None) -> Callable[[F], F]:
    if kind not in {"database", "http"}:
        raise ValueError("kind must be 'database' or 'http'")
    return _decorator(kind, name)


def record_llm_call(resp: LLMResponse) -> None:
    """Record bounded-cardinality measurements; content is opt-in."""
    if min(resp.input_tokens, resp.output_tokens) < 0 or resp.cost_usd < 0 or resp.latency_seconds < 0:
        raise ValueError("token counts, cost, and latency must be non-negative")
    outcome = "success" if resp.success else "error"
    llm_calls.labels(provider=resp.provider or "unknown", outcome=outcome).inc()
    llm_tokens.labels(kind="input").inc(resp.input_tokens)
    llm_tokens.labels(kind="output").inc(resp.output_tokens)
    llm_cost.inc(resp.cost_usd)
    llm_latency.observe(resp.latency_seconds)
    with _tracer.start_as_current_span("gen_ai.inference") as span:
        span.set_attribute("supportops.llm.provider", resp.provider or "unknown")
        span.set_attribute("supportops.llm.model", resp.model or "unknown")
        span.set_attribute("gen_ai.usage.input_tokens", resp.input_tokens)
        span.set_attribute("gen_ai.usage.output_tokens", resp.output_tokens)
        span.set_attribute("supportops.llm.cost_usd", resp.cost_usd)
        span.set_attribute("supportops.llm.latency_seconds", resp.latency_seconds)
        span.set_attribute("supportops.llm.success", resp.success)
        if _capture_content and resp.content is not None:
            span.set_attribute("supportops.llm.content", resp.content)
        if not resp.success:
            span.set_status(trace.Status(trace.StatusCode.ERROR))


def metrics_registry() -> CollectorRegistry:
    """Return this package's isolated Prometheus registry for scraping/testing."""
    return _registry


def record_agent_execution(*, steps: int, success: bool) -> None:
    if steps < 0:
        raise ValueError("steps must be non-negative")
    outcome = "success" if success else "error"
    task_steps.labels(outcome=outcome).observe(steps)
    task_success.labels(outcome=outcome).inc()


def record_tool_retry(tool: str) -> None:
    tool_retries.labels(tool=tool or "unknown").inc()


def record_loop_signal(reason: str) -> None:
    loop_signals.labels(reason=reason or "unknown").inc()
