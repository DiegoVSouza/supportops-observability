from pathlib import Path

import yaml


def test_required_alerts_cover_loop_cost_error_and_latency():
    root = Path(__file__).resolve().parents[1]
    data = yaml.safe_load((root / "alerts" / "observability.yml").read_text(encoding="utf-8"))
    rules = {rule["alert"]: rule for group in data["groups"] for rule in group["rules"]}
    assert {"AgentLoopDetected", "LLMCostAnomaly", "AgentErrorRateHigh", "LLMp95LatencyHigh"} <= rules.keys()
    assert "supportops_agent_loop_signals_total" in rules["AgentLoopDetected"]["expr"]
    assert "supportops_llm_cost_usd_total" in rules["LLMCostAnomaly"]["expr"]
    assert "supportops_llm_calls_total" in rules["AgentErrorRateHigh"]["expr"]
    assert "histogram_quantile(0.95" in rules["LLMp95LatencyHigh"]["expr"]
