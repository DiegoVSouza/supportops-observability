# P03 live LLM observability evaluation

## Status

Implemented and verified with a real completion. An in-memory exporter confirmed model/provider/usage fields and no response-content attribute; service validation remains incomplete without Docker/promtool.

## Goal and selection

Exercise P03's real OpenTelemetry/Prometheus instrumentation with one synthetic Groq SupportOps request. P03 is an observability product whose current LLM evidence is entirely fake; a real response will verify provider/model/token/latency metadata and content-safe tracing.

## Requirements

- Use optional official Groq SDK, model `openai/gpt-oss-20b`, and authenticated model-list preflight.
- One synthetic ticket and one completion, max 128 output tokens, 20s timeout, no parallel requests; explicit `LLM_MODE=live`.
- Load root `.env` without outputting keys. Bounded sequential retry/rotation for throttling and transient errors only; never fallback to another provider.
- Instrument the real response with `record_llm_call` under a `traced_agent` span; content capture remains disabled. Report actual model, provider token usage, latency, and trace/span counts. Billed cost is `PENDING` unless confirmed; do not claim synthetic or guessed cost.
- Preserve fake and synthetic incident traces, and keep P03 configured zero-dollar budget by using only the user-designated free-tier allowance.

## Acceptance

1. Offline mocked tests prove live-client sanitization and telemetry fields without network.
2. Existing instrumentation and full P03 checks continue to pass.
3. P03's `evals.capability` profile flag is enabled to reflect the added real capability evaluation.
4. A real call emits the expected LLM span and bounded Prometheus metrics, or saves a sanitized incomplete result.
5. No prompt, credentials, raw headers, or response body is saved.

## Scope

P03-local runner, tests, optional dependency, telemetry docs/evidence. No kit, service-stack changes, sibling projects, or production data.

## Verified references

- Model and response usage fields: [Groq GPT-OSS 20B](https://console.groq.com/docs/model/openai/gpt-oss-20b).
- Free-plan limits and throttling guidance: [Groq rate limits](https://console.groq.com/docs/rate-limits).
- Official SDK pinned in the optional live extra: [groq-python 1.7.0](https://github.com/groq/groq-python/releases/tag/v1.7.0).
