import json
import sqlite3
import subprocess
from contextlib import closing

import pytest

from scripts.local_operation import CASES, MANIFEST, LazySession, execute, fingerprint, validate
from supportops_obs.accounted import AccountedBlocked, _run


def test_fake_default_stops_before_manifest(monkeypatch, tmp_path):
    monkeypatch.setenv("LLM_MODE", "fake")
    with pytest.raises(AccountedBlocked, match="explicit_synthetic"):
        execute(CASES[0], project=tmp_path)
    assert not list(tmp_path.iterdir())


def test_lazy_startup_has_durable_reservation_and_no_new_id_bypass(tmp_path):
    path = tmp_path / "op.sqlite"
    def factory():
        with closing(sqlite3.connect(path)) as db:
            assert db.execute("SELECT status FROM attempts").fetchone()[0] == "reserved"
        raise TimeoutError("PRIVATE")
    with pytest.raises(AccountedBlocked, match="uncertain_attempt"):
        _run(path, CASES[0], LazySession(factory), campaign="local-operation-v1")
    with pytest.raises(AccountedBlocked, match="prior_work"):
        _run(path, CASES[1], LazySession(factory), campaign="local-operation-v1")


def test_manifest_requires_actual_committed_source(tmp_path):
    def git(*args):
        return subprocess.run(["git", *args], cwd=tmp_path, check=True, text=True, capture_output=True).stdout.strip()
    (tmp_path / "evals").mkdir()
    (tmp_path / "evals/live-execution.json").write_text(json.dumps({"execution_enabled": True}))
    (tmp_path / "pyproject.toml").write_text("fixture")
    git("init", "-q")
    git("config", "user.email", "fixture@example.invalid")
    git("config", "user.name", "Fixture")
    git("add", ".")
    git("commit", "-qm", "test: freeze source")
    target = tmp_path / MANIFEST
    target.parent.mkdir(parents=True)
    target.write_text(json.dumps({"project": "p03", "campaign_id": "local-operation-v1", "case_ids": CASES,
                                  "paid_usd": 0, "candidate": git("rev-parse", "HEAD"), "source_fingerprint": fingerprint(tmp_path)}))
    validate(tmp_path)
    (tmp_path / "pyproject.toml").write_text("changed")
    with pytest.raises(AccountedBlocked, match="source_provenance"):
        validate(tmp_path)
