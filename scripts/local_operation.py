"""Frozen synthetic single-call operation with accounted service telemetry."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

from supportops_obs import setup_telemetry, flush_telemetry, shutdown_telemetry
from supportops_obs.accounted import AccountedBlocked, _run

PROJECT = Path(__file__).resolve().parents[1]
LAB = PROJECT.parents[1]
MANIFEST = "artifacts/evals/live/local-operation-v1/manifest.json"
CASES = [f"fixture-local-{i:02}" for i in range(1, 5)]


def git(project, *args):
    result = subprocess.run(["git", *args], cwd=project, capture_output=True, timeout=15)
    if result.returncode:
        raise AccountedBlocked("source_provenance")
    return result.stdout.decode().strip()


def source_paths(project):
    return sorted(p for p in git(project, "ls-files").splitlines()
                  if p.startswith(("supportops_obs/", "scripts/", "tests/", "agent/", "evals/", "stack/", "alerts/"))
                  or p in {"pyproject.toml", "uv.lock", "harness.yaml"})


def fingerprint(project=PROJECT):
    paths = source_paths(project)
    if not paths:
        raise AccountedBlocked("source_provenance")
    git(project, "diff", "--quiet", "HEAD", "--", *paths)
    return hashlib.sha256(json.dumps([(p, hashlib.sha256((project / p).read_bytes()).hexdigest()) for p in paths],
                                     separators=(",", ":")).encode()).hexdigest()


def validate(project=PROJECT):
    try:
        manifest = json.loads((project / MANIFEST).read_text())
        owner = json.loads((project / "evals/live-execution.json").read_text())
    except (OSError, ValueError):
        raise AccountedBlocked("manifest_missing") from None
    if (manifest.get("project") != "p03" or manifest.get("campaign_id") != "local-operation-v1"
            or manifest.get("case_ids") != CASES or manifest.get("paid_usd") != 0
            or manifest.get("source_fingerprint") != fingerprint(project)
            or owner.get("execution_enabled") is not True):
        raise AccountedBlocked("manifest_mismatch")
    candidate = manifest.get("candidate")
    if not isinstance(candidate, str) or len(candidate) != 40:
        raise AccountedBlocked("candidate_missing")
    git(project, "merge-base", "--is-ancestor", candidate, "HEAD")
    git(project, "diff", "--quiet", candidate, "--", *source_paths(project))


class LazySession:
    provenance = "live"

    def __init__(self, factory):
        self.factory, self.session = factory, None

    def preview(self, envelope):
        self.session = self.factory()
        return self.session.preview(envelope)

    def complete(self, envelope):
        return self.session.complete(envelope)


def execute(request_id, *, project=PROJECT):
    if os.getenv("LLM_MODE", "fake") != "live" or request_id not in CASES:
        raise AccountedBlocked("explicit_synthetic_live_required")
    validate(project)
    sys.path.insert(0, str(LAB / "scripts/harness"))
    from live_free_account import machine_lease
    from live_provider_transport import ProviderSession
    policy = json.loads((LAB / "shared/policies/groq-free-campaign.json").read_text())
    if policy["projects"]["p03"]["requests"] != 160:
        raise AccountedBlocked("allocation_not_migrated")
    if not setup_telemetry("p03-accounted-local-live", otlp_endpoint="http://127.0.0.1:24317", capture_content=False):
        raise AccountedBlocked("telemetry_setup")
    path = project / "artifacts/evals/live/operations.sqlite"
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with machine_lease(LAB / ".runtime/llm-live-readiness/campaign.lock"):
            validate(project)
            result = _run(path, request_id, LazySession(lambda: ProviderSession(LAB, "p03", policy)), campaign="local-operation-v1")
            result["telemetry_flushed"] = flush_telemetry(timeout_millis=10000)
            return result
    finally:
        shutdown_telemetry()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fingerprint", action="store_true")
    parser.add_argument("--request-id", choices=CASES)
    args = parser.parse_args()
    try:
        if args.fingerprint:
            result = {"fingerprint": fingerprint()}
        elif args.request_id:
            result = execute(args.request_id)
        else:
            parser.error("--request-id or --fingerprint required")
        print(json.dumps(result))
        return 0 if result.get("telemetry_flushed", True) else 2
    except AccountedBlocked as error:
        print(json.dumps({"status": "INCOMPLETE", "reason": str(error)}))
        return 2
    except Exception:
        print(json.dumps({"status": "INCOMPLETE", "reason": "operation_uncertain"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
