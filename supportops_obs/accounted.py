"""Content-free telemetry for fixture sessions using the accounted protocol."""
import math
import re
import sqlite3
import time
from contextlib import closing
from decimal import Decimal

from .instrumentation import LLMResponse, record_llm_call, traced_agent

MODEL = "openai/gpt-oss-20b"


class AccountedBlocked(RuntimeError):
    """Fixed categorical errors, without transport messages."""


@traced_agent("accounted-operation")
def run(path, request_id, session):
    if getattr(session, "provenance", None) != "fixture":
        raise AccountedBlocked("fixture_session_required")
    if not isinstance(request_id, str) or not re.fullmatch(r"fixture-[A-Za-z0-9_-]{1,48}", request_id):
        raise AccountedBlocked("invalid_request")
    envelope = {"campaign_id": "fixture-telemetry-v1", "case_id": request_id,
                "trial": 1, "call_index": 1, "timeout_seconds": 20,
                "payload": {"model": MODEL, "messages": [
                    {"role": "system", "content": "Answer this local synthetic status question briefly."},
                    {"role": "user", "content": "Synthetic invoice status: pending. What is its status?"}],
                    "temperature": 0, "max_completion_tokens": 512,
                    "reasoning_effort": "low", "include_reasoning": False}}
    with closing(sqlite3.connect(path, timeout=5)) as db:
        db.execute("PRAGMA synchronous=FULL")
        db.execute("CREATE TABLE IF NOT EXISTS attempts(id TEXT PRIMARY KEY,status TEXT NOT NULL,receipt TEXT,input_tokens INTEGER,output_tokens INTEGER)")
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM attempts WHERE status!='ok'").fetchone():
            raise AccountedBlocked("prior_work_requires_review")
        if db.execute("SELECT 1 FROM attempts WHERE id=?", (request_id,)).fetchone():
            raise AccountedBlocked("already_reserved")
        if db.execute("SELECT COUNT(*) FROM attempts").fetchone()[0] >= 4:
            raise AccountedBlocked("allocation_exhausted")
        db.execute("INSERT INTO attempts(id,status) VALUES (?, 'reserved')", (request_id,))
        db.commit()
    started = time.monotonic()
    try:
        session.preview(envelope)
        result = session.complete(envelope)
    except Exception:
        raise AccountedBlocked("uncertain_attempt") from None
    usage = result.get("usage") if isinstance(result, dict) else None
    if (not isinstance(result, dict) or result.get("status") != "ok" or result.get("model") != MODEL
            or not isinstance(result.get("attempt_id"), str)
            or not re.fullmatch(r"[0-9a-f]{32}", result["attempt_id"])
            or not isinstance(usage, dict)
            or any(type(usage.get(key)) is not int or not 0 <= usage[key] <= cap
                   for key, cap in (("input_tokens", 4096), ("output_tokens", 512)))):
        raise AccountedBlocked("invalid_accounted_receipt")
    elapsed = time.monotonic() - started
    if not math.isfinite(elapsed) or elapsed < 0:
        raise AccountedBlocked("invalid_duration")
    with closing(sqlite3.connect(path, timeout=5)) as db:
        db.execute("PRAGMA synchronous=FULL")
        if db.execute("SELECT 1 FROM attempts WHERE receipt=?", (result["attempt_id"],)).fetchone():
            raise AccountedBlocked("duplicate_receipt")
        db.execute("UPDATE attempts SET status='ok',receipt=?,input_tokens=?,output_tokens=? WHERE id=? AND status='reserved'",
                   (result["attempt_id"], usage["input_tokens"], usage["output_tokens"], request_id))
        db.commit()
    cost = (Decimal(usage["input_tokens"]) * Decimal("0.075") + Decimal(usage["output_tokens"]) * Decimal("0.30")) / 1000000
    # Never pass content, arbitrary model/provider labels or receipt IDs to telemetry.
    record_llm_call(LLMResponse("groq", MODEL, usage["input_tokens"], usage["output_tokens"], float(cost), elapsed))
    return {"status": "ok", "provenance": "fixture", "receipt": result["attempt_id"],
            "input_tokens": usage["input_tokens"], "output_tokens": usage["output_tokens"]}
