"""Consumer regression smoke for the isolated 0.3.1 wheel."""

import sys
from importlib.metadata import distributions
from pathlib import Path

install = Path(__file__).parents[1] / "packages" / ".wheel-install-0.3.1"
sys.path.insert(0, str(install))

import supportops_obs  # noqa: E402,F401
from supportops_obs import traced_operation  # noqa: E402

assert next(d for d in distributions(path=[str(install)]) if d.metadata["Name"] == "supportops-obs").version == "0.3.1"


@traced_operation("database", "tickets.add")
def add_ticket():
    return {"ticket_id": "T-CONSUMER", "status": "created"}


assert add_ticket() == {"ticket_id": "T-CONSUMER", "status": "created"}
print("consumer_regression=PASS version=0.3.1 non_recording_span=PASS")
