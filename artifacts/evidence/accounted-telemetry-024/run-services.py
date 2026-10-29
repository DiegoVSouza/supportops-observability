import json
import os
import socket
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[3]
out = Path(__file__).resolve().parent
namespace = "p03-accounted-024-20261029"
env = dict(os.environ, LLM_MODE="fake", P03_COMPOSE_PROJECT=namespace,
           P03_CHECK_EVIDENCE_DIR="artifacts/evidence/accounted-telemetry-024/run",
           P03_SERVICE_EVIDENCE_DIR="artifacts/evidence/accounted-telemetry-024/run")
env["PYTEST_ADDOPTS"] = "--basetemp artifacts/evidence/accounted-telemetry-024/tmp-full-1"
records = []

def run(command, timeout=30):
    result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True, timeout=timeout)
    records.append({"command": command, "cwd": str(root), "exit_code": result.returncode, "output": result.stdout + result.stderr})
    (out / "commands-running.json").write_text(json.dumps(records, indent=2) + "\n", newline="\n")
    return result

def inventory():
    result = {}
    for kind, command in {
        "containers": ["docker", "ps", "-a", "--no-trunc", "--format", "{{.ID}}|{{.Names}}|{{.State}}"],
        "networks": ["docker", "network", "ls", "--no-trunc", "--format", "{{.ID}}|{{.Name}}"],
        "volumes": ["docker", "volume", "ls", "--format", "{{.Name}}"],
        "images": ["docker", "image", "ls", "--no-trunc", "--format", "{{.ID}}|{{.Repository}}:{{.Tag}}"],
    }.items():
        response = run(command)
        if response.returncode: raise RuntimeError("inventory_unavailable")
        result[kind] = sorted(response.stdout.splitlines())
    return result

compose = ["docker", "compose", "-p", namespace, "-f", "stack/docker-compose.obs.yml", "-f", "artifacts/evidence/phase-008-compose.override.yml", "-f", "stack/docker-compose.integration.yml"]
before = inventory()
(out / "inventory-before.json").write_text(json.dumps(before, indent=2) + "\n", newline="\n")
existing = run(["docker", "ps", "-a", "-q", "--filter", "label=com.docker.compose.project=" + namespace])
if existing.returncode or existing.stdout.strip(): raise RuntimeError("namespace_not_empty")
config = subprocess.run(compose + ["config", "--format", "json"], cwd=root, env=env, capture_output=True, text=True, timeout=30)
if config.returncode: raise RuntimeError("compose_config_failed")
services = json.loads(config.stdout)["services"]
ports = []
images = sorted({service["image"] for service in services.values() if "image" in service} | {"prom/prometheus:v3.14.0"})
for service in services.values():
    for port in service.get("ports", []):
        published = int(port["published"])
        with socket.socket() as probe:
            probe.bind(("127.0.0.1", published))
        ports.append(published)
for image in images:
    if run(["docker", "image", "inspect", image, "--format", "{{.Id}}"] ).returncode:
        raise RuntimeError("cached_image_missing")
(out / "preflight-current.json").write_text(json.dumps({"status": "PASS", "namespace": namespace, "images": images, "ports": ports}, indent=2) + "\n", newline="\n")
(out / "run").mkdir(exist_ok=True)
code = 2
try:
    result = run([sys.executable, "scripts/check_full.py"], timeout=1200)
    code = result.returncode
    if code == 0:
        probe = run([sys.executable, 'artifacts/evidence/accounted-telemetry-024/probe-export.py'], timeout=60)
        code = probe.returncode
finally:
    cleanup = run(compose + ["down", "--volumes", "--remove-orphans"], timeout=120)
    after = inventory()
    (out / "inventory-after.json").write_text(json.dumps(after, indent=2) + "\n", newline="\n")
    unchanged = all(set(before[kind]) <= set(after[kind]) for kind in before)
    remaining = run(["docker", "ps", "-a", "-q", "--filter", "label=com.docker.compose.project=" + namespace])
    report = {"gate_exit_code": code, "cleanup_exit_code": cleanup.returncode, "prior_resources_preserved": unchanged, "phase_containers_remaining": bool(remaining.stdout.strip()), "provider_calls": 0}
    (out / "service-result.json").write_text(json.dumps(report, indent=2) + "\n", newline="\n")
    print(json.dumps(report))
    if cleanup.returncode or not unchanged or remaining.stdout.strip(): code = 1
sys.exit(code)
