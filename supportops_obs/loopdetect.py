"""Deterministic repeated-action, state-cycle and step-limit detector."""

from __future__ import annotations

import hashlib
import json
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class StepRecord:
    tool: str | None = None
    arguments: object = None
    state: str | None = None
    step_number: int = 0


@dataclass(frozen=True)
class LoopSignal:
    detected: bool
    reason: str | None = None
    repeated_count: int = 0


class LoopDetector:
    def __init__(self, *, repeat_threshold: int = 3, cycle_threshold: int = 3, max_steps: int = 40, history_size: int = 128) -> None:
        if repeat_threshold < 2 or cycle_threshold < 2 or max_steps < 1 or history_size < 2:
            raise ValueError("thresholds and limits must be positive; repeat/cycle thresholds must be >= 2")
        self.repeat_threshold = repeat_threshold
        self.cycle_threshold = cycle_threshold
        self.max_steps = max_steps
        self._actions: deque[str] = deque(maxlen=history_size)
        self._states: deque[str] = deque(maxlen=history_size)
        self._count = 0

    def reset(self) -> None:
        self._actions.clear()
        self._states.clear()
        self._count = 0

    def observe(self, step: StepRecord) -> LoopSignal:
        if step.step_number < 0:
            raise ValueError("step_number must be non-negative")
        self._count += 1
        if step.tool is not None:
            try:
                normalized = json.dumps(step.arguments, sort_keys=True, separators=(",", ":"))
            except (TypeError, ValueError) as exc:
                raise ValueError("tool arguments must be JSON-serializable") from exc
            digest = hashlib.sha256(normalized.encode()).hexdigest()
            action = f"{step.tool}:{digest}"
            self._actions.append(action)
            if len(self._actions) >= self.repeat_threshold and len(set(list(self._actions)[-self.repeat_threshold:])) == 1:
                return self._signal("repeated_tool_arguments", self.repeat_threshold)
        if step.state is not None:
            self._states.append(step.state)
            states = list(self._states)
            for cycle_len in range(1, len(states) // self.cycle_threshold + 1):
                tail = states[-cycle_len * self.cycle_threshold:]
                if all(tail[i:i + cycle_len] == tail[:cycle_len] for i in range(0, len(tail), cycle_len)):
                    return self._signal("state_cycle", cycle_len * self.cycle_threshold)
        if self._count > self.max_steps:
            return self._signal("step_limit", self._count)
        return LoopSignal(False)

    @staticmethod
    def _signal(reason: str, count: int) -> LoopSignal:
        from .instrumentation import record_loop_signal
        record_loop_signal(reason)
        return LoopSignal(True, reason, count)
