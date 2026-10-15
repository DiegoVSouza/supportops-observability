"""Run deterministic package tests and structural configuration validation."""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "artifacts" / "evidence" / "check-full.txt"
EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
lines: list[str] = []
failures = 0
incomplete: list[str] = []


def gate_status(failures: int, incomplete_gates: list[str]) -> tuple[str, int]:
    if failures:
        return "FAIL", 1
    if incomplete_gates:
        return "INCOMPLETE", 2
    return "PASS", 0


def record(command: str, code: int, output: str) -> None:
    lines.extend((f"$ {command}", f"exit_code={code}", output.rstrip() or "(no output)", ""))


def run(command: list[str], label: str) -> int:
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    record(label, result.returncode, result.stdout + result.stderr)
    return result.returncode


def main() -> int:
    global failures
    try:
        import yaml
    except ImportError:
        record("import yaml", 1, "PyYAML missing; run uv sync --extra dev")
        failures += 1
    else:
        for path in sorted((ROOT / "stack").rglob("*.yml")) + sorted((ROOT / "alerts").rglob("*.yml")):
            try:
                yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception as exc:
                record(f"parse YAML {path.relative_to(ROOT)}", 1, str(exc))
                failures += 1
            else:
                record(f"parse YAML {path.relative_to(ROOT)}", 0, "valid YAML")
        try:
            json.loads((ROOT / "dashboards" / "supportops-overview.json").read_text(encoding="utf-8"))
            json.loads((ROOT / "docs" / "harness" / "sources.lock.json").read_text(encoding="utf-8"))
            for path in (ROOT / "incident-lab").glob("*.json"):
                json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            record("validate JSON artifacts", 1, str(exc))
            failures += 1
        else:
            record("validate JSON artifacts", 0, "dashboard, source lock and incident fixtures valid")

    result = subprocess.run([sys.executable, "-m", "pytest", "tests"], cwd=ROOT, capture_output=True, text=True)
    record(f"{sys.executable} -m pytest tests", result.returncode, result.stdout + result.stderr)
    failures += int(result.returncode != 0)
    failures += int(run([sys.executable, "demo/runner_double.py", "--once"], "LLM_MODE=fake python demo/runner_double.py --once") != 0)
    failures += int(run([sys.executable, "incident-lab/simulate.py"], "python incident-lab/simulate.py") != 0)
    if shutil.which("promtool"):
        failures += int(run(["promtool", "check", "rules", "alerts/observability.yml"], "promtool check rules alerts/observability.yml") != 0)
    else:
        incomplete.append("promtool rule validation: executable unavailable")
        record("promtool check rules alerts/observability.yml", 127, "INCOMPLETE: promtool unavailable")
    docker = shutil.which("docker")
    if docker:
        failures += int(run([docker, "compose", "-f", "stack/docker-compose.obs.yml", "config", "--quiet"], "docker compose config --quiet") != 0)
        incomplete.append("dashboard and incident service E2E not executed by this structural gate")
    else:
        incomplete.append("Docker Compose validation: executable unavailable")
        record("docker compose config --quiet", 127, "INCOMPLETE: docker unavailable")
        incomplete.append("dashboard and incident service E2E: Docker unavailable")
    if shutil.which("uv"):
        failures += int(run(["uv", "lock", "--check"], "uv lock --check") != 0)
    else:
        incomplete.append("lockfile consistency: uv unavailable")
        record("uv lock --check", 127, "INCOMPLETE: uv unavailable")
    status, exit_code = gate_status(failures, incomplete)
    lines.append(f"result={status}; failures={failures}; incomplete={'; '.join(incomplete) if incomplete else 'none'}")
    lines.append(f"outer_exit_code={exit_code}")
    EVIDENCE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"check-full: {status}; failures={failures}; incomplete={len(incomplete)}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
