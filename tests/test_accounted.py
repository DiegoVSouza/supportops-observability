import sqlite3
from contextlib import closing
from pathlib import Path

import pytest
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

import supportops_obs.instrumentation as inst
from supportops_obs.accounted import MODEL, AccountedBlocked, run


class Session:
    provenance = "fixture"

    def __init__(self):
        self.calls = 0
        self.result = {"status": "ok", "model": MODEL, "attempt_id": "a" * 32,
                       "usage": {"input_tokens": 101, "output_tokens": 19},
                       "content": "SECRET response", "tool_calls": [{"SECRET": "key"}]}

    def preview(self, envelope):
        pass

    def complete(self, envelope):
        self.calls += 1
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def test_exact_usage_correlated_without_content_even_when_capture_enabled(tmp_path, monkeypatch):
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    monkeypatch.setattr(inst, "_tracer", provider.get_tracer("accounted-test"))
    monkeypatch.setattr(inst, "_capture_content", True)
    result = run(tmp_path / "op.sqlite", "fixture-one", Session())
    spans = {span.name: span for span in exporter.get_finished_spans()}
    parent, child = spans["agent.accounted-operation"], spans["llm.inference"]
    assert child.parent.span_id == parent.context.span_id
    assert child.context.trace_id == parent.context.trace_id
    assert child.attributes["supportops.llm.input_tokens"] == 101
    assert child.attributes["supportops.llm.output_tokens"] == 19
    assert result["input_tokens"] == 101
    assert "SECRET" not in str([(dict(span.attributes), span.events, span.status.description) for span in spans.values()])
    assert "a" * 32 not in str([dict(span.attributes) for span in spans.values()])
    provider.shutdown()


def test_reservation_committed_before_dispatch_and_no_replay(tmp_path):
    path = tmp_path / "op.sqlite"
    session = Session()
    def preview(envelope):
        with closing(sqlite3.connect(path)) as db:
            assert db.execute("SELECT status FROM attempts").fetchone()[0] == "reserved"
    session.preview = preview
    run(path, "fixture-one", session)
    with pytest.raises(AccountedBlocked, match="already_reserved"):
        run(path, "fixture-one", session)
    assert session.calls == 1


def test_uncertain_restart_blocks_new_identity(tmp_path):
    path = tmp_path / "op.sqlite"
    session = Session()
    session.result = TimeoutError("SECRET")
    with pytest.raises(AccountedBlocked, match="uncertain_attempt"):
        run(path, "fixture-one", session)
    with pytest.raises(AccountedBlocked, match="prior_work"):
        run(path, "fixture-two", Session())


@pytest.mark.parametrize("bad", [True, -1, 4097, None, float("nan")])
def test_bad_usage_stays_reserved(tmp_path, bad):
    session = Session()
    session.result["usage"]["input_tokens"] = bad
    with pytest.raises(AccountedBlocked, match="invalid_accounted"):
        run(tmp_path / "op.sqlite", "fixture-one", session)


def test_live_provenance_refused_before_reservation(tmp_path):
    session = Session()
    session.provenance = "live"
    path = tmp_path / "op.sqlite"
    with pytest.raises(AccountedBlocked, match="fixture_session"):
        run(path, "fixture-one", session)
    assert not path.exists()


def test_grafana_compose_wait_requires_http_readiness():
    import yaml
    config = yaml.safe_load((Path(__file__).resolve().parents[1] / "stack/docker-compose.obs.yml").read_text())
    health = config["services"]["grafana"]["healthcheck"]
    assert health["test"][0] == "CMD-SHELL"
    assert "http://127.0.0.1:3000/api/health" in health["test"][1]
    assert health["retries"] > 0 and health["timeout"] == "3s"
