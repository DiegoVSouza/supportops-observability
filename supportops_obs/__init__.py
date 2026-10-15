"""OpenTelemetry instrumentation and loop detection for agent workflows."""

from .instrumentation import LLMResponse, flush_telemetry, metrics_registry, record_agent_execution, record_llm_call, record_tool_retry, setup_telemetry, shutdown_telemetry, traced_agent, traced_operation, traced_tool
from .loopdetect import LoopDetector, LoopSignal, StepRecord

__all__ = [
    "LLMResponse",
    "flush_telemetry",
    "LoopDetector",
    "LoopSignal",
    "StepRecord",
    "metrics_registry",
    "record_agent_execution",
    "record_llm_call",
    "record_tool_retry",
    "setup_telemetry",
    "shutdown_telemetry",
    "traced_agent",
    "traced_operation",
    "traced_tool",
]
