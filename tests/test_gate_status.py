from scripts.check_full import gate_status


def test_missing_required_validator_is_incomplete_and_nonzero():
    assert gate_status(0, ["promtool unavailable"]) == ("INCOMPLETE", 2)


def test_executed_failure_takes_precedence_over_incomplete():
    assert gate_status(1, ["Docker unavailable"]) == ("FAIL", 1)


def test_all_required_gates_passing_returns_zero():
    assert gate_status(0, []) == ("PASS", 0)
