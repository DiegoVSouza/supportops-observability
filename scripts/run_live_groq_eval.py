"""One synthetic Groq completion recorded through the observability API."""
from __future__ import annotations
import json, os, random, time
from datetime import UTC, datetime
from pathlib import Path
from groq import Groq
import supportops_obs.instrumentation as inst
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from supportops_obs import LLMResponse, record_llm_call

PROJECT=Path(__file__).resolve().parents[1]
LAB=Path(__file__).resolve().parents[3]
MODEL="openai/gpt-oss-20b"

def credentials():
    env=LAB/".env"
    for line in env.read_text(encoding="utf-8").splitlines():
        if line.strip() and not line.lstrip().startswith("#") and "=" in line:
            name,value=line.split("=",1); name=name.strip()
            if name.startswith("GROQ_API_KEY") and value.strip() and name not in os.environ: os.environ[name]=value.strip().strip("\"'")
    return list(dict.fromkeys(os.getenv(n,"").strip() for n in [f"GROQ_API_KEY_{i}" for i in range(1,5)] if os.getenv(n,"")))

def call(keys):
    available=[]
    for key in keys:
        client=Groq(api_key=key,max_retries=0,timeout=20)
        if any(m.id==MODEL for m in client.models.list().data): available.append(key)
    if not available: raise RuntimeError("model unavailable in authenticated catalog")
    prompt="A synthetic support agent receives: 'How do I find the tracking link for a delayed parcel?' Return a concise policy answer that does not claim a live lookup."
    for attempt,key in enumerate(available[:4]):
        client=Groq(api_key=key,max_retries=0,timeout=20)
        try:
            start=time.perf_counter()
            response=client.chat.completions.create(model=MODEL,messages=[{"role":"user","content":prompt}],max_completion_tokens=128,reasoning_effort="low",temperature=1)
            return response,round(time.perf_counter()-start,6),len(available)
        except Exception as exc:
            status=getattr(exc,"status_code",None)
            if status not in {408,409,429,500,502,503,504} and type(exc).__name__ not in {"Timeout","APIConnectionError"}: raise RuntimeError(f"provider rejection: {type(exc).__name__}, status={status}") from None
            if attempt>=min(3,len(available)-1): raise RuntimeError(f"transient retries exhausted: {type(exc).__name__}, status={status}") from None
            headers=getattr(getattr(exc,"response",None),"headers",{})
            try: delay=float(headers.get("retry-after")) if status==429 and headers.get("retry-after") else min(.25*(2**attempt)+random.random()*.1,2)
            except (ValueError,TypeError): delay=min(.25*(2**attempt)+random.random()*.1,2)
            if not 0<=delay<=2: raise RuntimeError("retry-after exceeds 2 second cap") from None
            time.sleep(delay)

def main():
    result={"provider":"groq","model":MODEL,"status":"INCOMPLETE","exit_code":1,"started_at_utc":datetime.now(UTC).isoformat(),"content_capture":False}
    code=1
    try:
        if os.getenv("LLM_MODE","").lower()!="live": raise RuntimeError("explicit LLM_MODE=live required")
        keys=credentials(); result["credential_count"]=len(keys)
        response,latency,key_count=call(keys); usage=response.usage
        exporter=InMemorySpanExporter(); provider=TracerProvider(); provider.add_span_processor(SimpleSpanProcessor(exporter)); inst._tracer=provider.get_tracer("supportops_obs.live")
        estimated_cost=(usage.prompt_tokens*.075+usage.completion_tokens*.30)/1_000_000
        record_llm_call(LLMResponse("groq",MODEL,usage.prompt_tokens,usage.completion_tokens,estimated_cost,latency,content=None))
        spans=exporter.get_finished_spans(); attrs=spans[-1].attributes if spans else {}
        checks={"span_recorded":bool(spans),"provider":attrs.get("supportops.llm.provider")=="groq","model":attrs.get("supportops.llm.model")==MODEL,"usage":attrs.get("supportops.llm.input_tokens")==usage.prompt_tokens and attrs.get("supportops.llm.output_tokens")==usage.completion_tokens,"content_absent":all("content" not in k for span in spans for k in span.attributes)}
        code=0 if all(checks.values()) else 1
        result.update(status="PASS" if code==0 else "FAIL",assertions=checks,model_available_key_count=key_count,input_tokens=usage.prompt_tokens,output_tokens=usage.completion_tokens,latency_seconds=latency,estimated_cost_usd=estimated_cost,cost_usd="PENDING",span_count=len(spans),metrics_recorded=True)
        provider.shutdown()
    except Exception as exc:
        result["error"]={"class":type(exc).__name__}
        code=1
    result.update(exit_code=code,finished_at_utc=datetime.now(UTC).isoformat())
    out=PROJECT/"artifacts"/"evidence"; out.mkdir(parents=True,exist_ok=True); stamp=datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
    (out/f"phase-010-groq-{stamp}.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    (out/f"phase-010-groq-{stamp}.txt").write_text(f"Command: LLM_MODE=live uv run --extra live --extra dev python scripts/run_live_groq_eval.py\nExit code: {code}\nSanitized result: {json.dumps(result,sort_keys=True)}\n",encoding="utf-8")
    print(json.dumps(result,sort_keys=True)); return code

if __name__=="__main__": raise SystemExit(main())
