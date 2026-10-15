"""OpenTelemetry instrumentation and loop detection for agent workflows."""

from .instrumentation import LLMResponse, metrics_registry, record_agent_execution, record_llm_call, record_tool_retry, setup_telemetry, traced_agent, traced_operation, traced_tool
from .loopdetect import LoopDetector, LoopSignal, StepRecord

__all__ = [
    "LLMResponse",
    "LoopDetector",
    "LoopSignal",
    "StepRecord",
    "metrics_registry",
    "record_agent_execution",
    "record_llm_call",
    "record_tool_retry",
    "setup_telemetry",
    "traced_agent",
    "traced_operation",
    "traced_tool",
]
