"""Run deterministic package tests and structural configuration validation."""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import os

ROOT = pathlib.Path(__file__).resolve().parents[1]


def evidence_dir() -> pathlib.Path:
    root = (ROOT / "artifacts" / "evidence").resolve()
    configured = (ROOT / os.getenv("P03_CHECK_EVIDENCE_DIR", "artifacts/evidence")).resolve()
    if not configured.is_relative_to(root):
        raise ValueError("P03_CHECK_EVIDENCE_DIR must be inside artifacts/evidence")
    configured.mkdir(parents=True, exist_ok=True)
    return configured


try:
    EVIDENCE_DIR = evidence_dir()
except (OSError, ValueError) as exc:
    print(f"check-full: FAIL unsafe evidence directory: {exc}")
    sys.exit(1)

EVIDENCE = EVIDENCE_DIR / "check-full.txt"
lines: list[str] = []
failures = 0
incomplete: list[str] = []


def gate_status(failures: int, incomplete_gates: list[str]) -> tuple[str, int]:
    if failures:
        return "FAIL", 1
    if incomplete_gates:
        return "INCOMPLETE", 2
    return "PASS", 0


def rule_commands(native: str | None, docker_ready: bool) -> list[list[str]]:
    if docker_ready:
        base=["docker","run","--rm","--entrypoint","promtool","-v",f"{ROOT / 'alerts'}:/rules:ro",
              "-v",f"{ROOT / 'tests' / 'fixtures' / 'alert_rules.yml'}:/tests.yml:ro","prom/prometheus:v3.14.0"]
        return [base+["check","rules","/rules/observability.yml"],base+["test","rules","/tests.yml"]]
    if native:
        fixture=(ROOT/'tests/fixtures/alert_rules.yml').read_text().replace('/rules/observability.yml',str(ROOT/'alerts/observability.yml').replace('\\','/'))
        target=EVIDENCE_DIR/'phase-009-native-alert-tests.yml'
        target.write_text(fixture)
        return [[native,'check','rules','alerts/observability.yml'],[native,'test','rules',str(target)]]
    return []


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
    failures += int(run([sys.executable, "demo/integrated_trace.py"], "python demo/integrated_trace.py (synthetic local exporter)") != 0)
    failures += int(run([sys.executable, "incident-lab/simulate.py"], "python incident-lab/simulate.py") != 0)
    docker = shutil.which("docker")
    docker_ready=bool(docker and subprocess.run([docker,'info','--format','{{.ServerVersion}}'],capture_output=True).returncode==0)
    validators=rule_commands(shutil.which('promtool'),docker_ready)
    for command in validators:
        failures+=int(run(command,' '.join(command))!=0)
    if not validators:
        incomplete.append("promtool rule validation: executable unavailable")
        record("promtool check rules alerts/observability.yml", 127, "INCOMPLETE: promtool unavailable")
    if docker:
        failures += int(run([docker, "compose", "-f", "stack/docker-compose.obs.yml", "config", "--quiet"], "docker compose config --quiet") != 0)
    else:
        incomplete.append("Docker Compose validation: executable unavailable")
        record("docker compose config --quiet", 127, "INCOMPLETE: docker unavailable")
    if os.getenv('P03_SKIP_SERVICES')=='1':
        incomplete.append('required service gate explicitly not executed')
        record('service integration',127,'INCOMPLETE: required service gate not executed')
    else:
        service_rc=run([sys.executable,'scripts/check_services.py'],'python scripts/check_services.py')
        if service_rc==2: incomplete.append('required service integration unavailable or incomplete')
        elif service_rc: failures+=1
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
