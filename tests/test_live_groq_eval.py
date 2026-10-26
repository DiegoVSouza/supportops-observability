from types import SimpleNamespace

from opentelemetry.sdk.trace.export import SpanExportResult


def test_live_response_exports_content_safe_agent_and_llm_spans(monkeypatch):
    from scripts import run_live_groq_eval as evaluation

    exported = []

    class Exporter:
        def __init__(self, **kwargs):
            assert kwargs["endpoint"] == "http://127.0.0.1:24317"

        def export(self, spans):
            exported.extend(spans)
            return SpanExportResult.SUCCESS

        def shutdown(self):
            pass

    monkeypatch.setenv("P03_LIVE_OTLP_ENDPOINT", "http://127.0.0.1:24317")
    monkeypatch.setattr(evaluation, "OTLPSpanExporter", Exporter, raising=False)
    response = SimpleNamespace(
        usage=SimpleNamespace(prompt_tokens=2, completion_tokens=3)
    )
    summary = evaluation.record_response(response, 0.1)
    assert summary["status"] == "PASS"
    assert summary["trace_id"]
    assert {span.name for span in exported} == {
        "agent.live-evaluation",
        "llm.inference",
    }
    assert all("supportops.llm.content" not in span.attributes for span in exported)
