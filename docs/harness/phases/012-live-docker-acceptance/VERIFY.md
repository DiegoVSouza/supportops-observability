# Verification

Result: PASS for the scoped acceptance.

The first Docker gate exceeded its cold-start synthetic-alert wait. All four alerts later fired; increasing the configurable wait to 600 seconds preserved thresholds. The subsequent full gate passed with no incomplete checks. A real Groq completion (103 input / 64 output tokens) exported parent and inference spans over OTLP. Jaeger independently confirmed provider, model, usage and absent content.

Evidence: artifacts/evidence/live-docker/ contains executed commands, exit codes, retained failed attempts and sanitized results. Timestamped phase Groq reports are additional real-run evidence. Historical reports are preserved.

Every live run authenticated the requested model catalog before generation. Model: openai/gpt-oss-20b; official Groq SDK: 1.7.0; Docker Engine: 29.1.3. Only numbered root credentials were read silently. No silent fake fallback, paid provider fallback, kit edits, push, refunds or outbound customer messages occurred. Estimated costs derive only from observed usage; billed cost remains PENDING. This small synthetic sample does not establish general model quality.

Fake remains the default. Service integration checks use dedicated Compose projects. All 28 pre-existing container names are still present; this is not a health claim about unrelated stacks. Newly started live stacks are left available.
