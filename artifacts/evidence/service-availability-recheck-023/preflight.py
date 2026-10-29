import json
import subprocess
import sys
from pathlib import Path

project = Path(__file__).resolve().parents[3]
command = ["docker", "info", "--format", "{{.ServerVersion}}"]
try:
    result = subprocess.run(command, cwd=project, capture_output=True, text=True, timeout=15)
    report = {"command": "docker info --format {{.ServerVersion}}", "cwd": str(project), "exit_code": result.returncode, "output": result.stdout + result.stderr, "status": "PASS" if result.returncode == 0 else "INCOMPLETE"}
except (OSError, subprocess.TimeoutExpired) as error:
    report = {"command": "docker info --format {{.ServerVersion}}", "cwd": str(project), "exit_code": 2, "output": type(error).__name__, "status": "INCOMPLETE"}
if report["status"] != "PASS":
    report["stop"] = "docker_daemon_unavailable; no resources started; images, ports and namespace not assessed"
(Path(__file__).resolve().parent / "preflight.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
print(json.dumps(report, indent=2))
sys.exit(0 if report["status"] == "PASS" else 2)
