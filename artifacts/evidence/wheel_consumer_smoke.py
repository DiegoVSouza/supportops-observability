"""Isolated local wheel consumer smoke; imports only from the target install."""

import sys
from importlib.metadata import distributions
from pathlib import Path

install = Path(__file__).parents[1] / "packages" / ".wheel-install-0.3.0"
sys.path.insert(0, str(install))

import supportops_obs  # noqa: E402
from supportops_obs import record_agent_execution, record_tool_retry  # noqa: E402

assert next(d for d in distributions(path=[str(install)]) if d.metadata["Name"] == "supportops-obs").version == "0.3.0"
record_agent_execution(steps=2, success=True, task_type="billing", cost_usd=0.02)
record_tool_retry("ticket_lookup", task_type="billing")
print("consumer_smoke=PASS version=0.3.0 exports=PASS")
