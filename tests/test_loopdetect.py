import pytest

from supportops_obs import LoopDetector, StepRecord


def test_repeated_tool_and_arguments_detected():
    detector = LoopDetector(repeat_threshold=3)
    assert not detector.observe(StepRecord(tool="search", arguments={"q": "one"})).detected
    assert not detector.observe(StepRecord(tool="search", arguments={"q": "one"})).detected
    signal = detector.observe(StepRecord(tool="search", arguments={"q": "one"}))
    assert signal.detected and signal.reason == "repeated_tool_arguments"


def test_argument_order_is_normalized_but_distinct_arguments_are_not():
    detector = LoopDetector(repeat_threshold=3)
    detector.observe(StepRecord(tool="search", arguments={"a": 1, "b": 2}))
    detector.observe(StepRecord(tool="search", arguments={"b": 2, "a": 1}))
    assert detector.observe(StepRecord(tool="search", arguments={"a": 1, "b": 2})).detected
    distinct = LoopDetector(repeat_threshold=3)
    for q in ("a", "b", "c"):
        assert not distinct.observe(StepRecord(tool="search", arguments={"q": q})).detected


def test_repeating_state_cycle_and_healthy_path():
    detector = LoopDetector(cycle_threshold=3)
    for state in ("plan", "act", "observe") * 3:
        signal = detector.observe(StepRecord(state=state))
    assert signal.detected and signal.reason == "state_cycle"

    healthy = LoopDetector(repeat_threshold=3, cycle_threshold=3, max_steps=10)
    for i, (tool, state) in enumerate((("lookup", "start"), ("classify", "found"), ("reply", "done")), start=1):
        assert not healthy.observe(StepRecord(tool=tool, arguments={"i": i}, state=state)).detected


def test_step_limit_boundary_and_reset():
    detector = LoopDetector(max_steps=2)
    assert not detector.observe(StepRecord(state="a")).detected
    assert not detector.observe(StepRecord(state="b")).detected
    signal = detector.observe(StepRecord(state="c"))
    assert signal.detected and signal.reason == "step_limit" and signal.repeated_count == 3
    detector.reset()
    assert not detector.observe(StepRecord(state="a")).detected


@pytest.mark.parametrize("kwargs", [{"repeat_threshold": 1}, {"cycle_threshold": 1}, {"max_steps": 0}, {"history_size": 1}])
def test_invalid_limits_rejected(kwargs):
    with pytest.raises(ValueError):
        LoopDetector(**kwargs)


def test_negative_step_number_rejected():
    with pytest.raises(ValueError):
        LoopDetector().observe(StepRecord(step_number=-1))


def test_non_json_tool_arguments_rejected_without_consuming_step():
    detector = LoopDetector(max_steps=1)
    with pytest.raises(ValueError):
        detector.observe(StepRecord(tool="search", arguments={"unsupported": object()}))
    assert not detector.observe(StepRecord(state="healthy")).detected
