"""One synthetic Groq completion recorded through the observability API."""

from __future__ import annotations

import json
import os
import random
import time
from datetime import UTC, datetime
from pathlib import Path

from groq import Groq
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

import supportops_obs.instrumentation as inst
from supportops_obs import LLMResponse, record_llm_call

PROJECT = Path(__file__).resolve().parents[1]
LAB = Path(__file__).resolve().parents[3]
MODEL = "openai/gpt-oss-20b"


def load_credentials() -> list[str]:
    env_path = LAB / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#") and "=" in line:
            name, value = line.split("=", 1)
            name = name.strip()
            if (
                name.startswith("GROQ_API_KEY")
                and value.strip()
                and name not in os.environ
            ):
                os.environ[name] = value.strip().strip("\"'")
    return list(
        dict.fromkeys(
            os.getenv(n, "").strip()
            for n in [f"GROQ_API_KEY_{i}" for i in range(1, 5)]
            if os.getenv(n, "")
        )
    )


def available_model_keys(api_keys: list[str]) -> list[str]:
    available = []
    for key in api_keys:
        client = Groq(api_key=key, max_retries=0, timeout=20)
        if any(m.id == MODEL for m in client.models.list().data):
            available.append(key)
    if not available:
        raise RuntimeError("model unavailable in authenticated catalog")
    return available


def retry_delay(attempt: int, status: int | None, headers) -> float:
    try:
        delay = (
            float(headers.get("retry-after"))
            if status == 429 and headers.get("retry-after")
            else min(0.25 * (2**attempt) + random.random() * 0.1, 2)
        )
    except (ValueError, TypeError):
        delay = min(0.25 * (2**attempt) + random.random() * 0.1, 2)
    if not 0 <= delay <= 2:
        raise RuntimeError("retry-after exceeds 2 second cap") from None
    return delay


def request_completion(api_keys: list[str]):
    available = available_model_keys(api_keys)
    prompt = "A synthetic support agent receives: 'How do I find the tracking link for a delayed parcel?' Return a concise policy answer that does not claim a live lookup."
    for attempt, key in enumerate(available[:4]):
        client = Groq(api_key=key, max_retries=0, timeout=20)
        try:
            start = time.perf_counter()
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=128,
                reasoning_effort="low",
                temperature=1,
            )
            return response, round(time.perf_counter() - start, 6), len(available)
        except Exception as exc:
            status = getattr(exc, "status_code", None)
            if status not in {408, 409, 429, 500, 502, 503, 504} and type(
                exc
            ).__name__ not in {"Timeout", "APIConnectionError"}:
                raise RuntimeError(
                    f"provider rejection: {type(exc).__name__}, status={status}"
                ) from None
            if attempt >= min(3, len(available) - 1):
                raise RuntimeError(
                    f"transient retries exhausted: {type(exc).__name__}, status={status}"
                ) from None
            headers = getattr(getattr(exc, "response", None), "headers", {})
            delay = retry_delay(attempt, status, headers)
            time.sleep(delay)


def record_response(response, latency: float) -> dict[str, object]:
    usage = response.usage
    actual_model = getattr(response, "model", MODEL)
    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    endpoint = os.getenv("P03_LIVE_OTLP_ENDPOINT")
    if endpoint:
        provider.add_span_processor(
            SimpleSpanProcessor(
                OTLPSpanExporter(
                    endpoint=endpoint, insecure=endpoint.startswith("http://")
                )
            )
        )
    previous_tracer = inst._tracer
    inst._tracer = provider.get_tracer("supportops_obs.live")
    estimated_cost = (
        usage.prompt_tokens * 0.075 + usage.completion_tokens * 0.30
    ) / 1_000_000
    try:
        with inst._tracer.start_as_current_span("agent.live-evaluation") as parent:
            record_llm_call(
                LLMResponse(
                    "groq",
                    actual_model,
                    usage.prompt_tokens,
                    usage.completion_tokens,
                    estimated_cost,
                    latency,
                    content=None,
                )
            )
        if not provider.force_flush():
            raise RuntimeError("live trace flush did not complete")
        spans = exporter.get_finished_spans()
        inference = next((span for span in spans if span.name == "llm.inference"), None)
        attrs = inference.attributes if inference else {}
        checks = {
            "span_recorded": inference is not None,
            "provider": attrs.get("supportops.llm.provider") == "groq",
            "model": attrs.get("supportops.llm.model") == MODEL,
            "usage": attrs.get("supportops.llm.input_tokens") == usage.prompt_tokens
            and attrs.get("supportops.llm.output_tokens") == usage.completion_tokens,
            "content_absent": all(
                "content" not in key for span in spans for key in span.attributes
            ),
        }
        return dict(
            status="PASS" if all(checks.values()) else "FAIL",
            assertions=checks,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            latency_seconds=latency,
            estimated_cost_usd=estimated_cost,
            cost_usd="PENDING",
            span_count=len(spans),
            metrics_recorded=True,
            actual_model=actual_model,
            trace_id=format(parent.get_span_context().trace_id, "032x"),
            otlp_export_enabled=bool(endpoint),
        )
    finally:
        inst._tracer = previous_tracer
        provider.shutdown()


def write_result(result: dict[str, object], code: int) -> None:
    evidence_dir = PROJECT / "artifacts" / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    (evidence_dir / f"phase-010-groq-{timestamp}.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    (evidence_dir / f"phase-010-groq-{timestamp}.txt").write_text(
        f"Command: LLM_MODE=live uv run --extra live --extra dev python scripts/run_live_groq_eval.py\nExit code: {code}\nSanitized result: {json.dumps(result, sort_keys=True)}\n",
        encoding="utf-8",
    )


def main() -> int:
    result = {
        "provider": "groq",
        "model": MODEL,
        "status": "INCOMPLETE",
        "exit_code": 1,
        "started_at_utc": datetime.now(UTC).isoformat(),
        "content_capture": False,
    }
    code = 1
    try:
        if os.getenv("LLM_MODE", "").lower() != "live":
            raise RuntimeError("explicit LLM_MODE=live required")
        api_keys = load_credentials()
        result["credential_count"] = len(api_keys)
        response, latency, key_count = request_completion(api_keys)
        result.update(record_response(response, latency))
        result["model_available_key_count"] = key_count
        code = 0 if result["status"] == "PASS" else 1
    except Exception as exc:
        result["error"] = {"class": type(exc).__name__}
        code = 1
    result.update(exit_code=code, finished_at_utc=datetime.now(UTC).isoformat())
    write_result(result, code)
    print(json.dumps(result, sort_keys=True))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
