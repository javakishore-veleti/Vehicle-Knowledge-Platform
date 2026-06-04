# guardrails-service

FastAPI **input + output guardrails** for the VKP LLM search pipeline, with a Postgres **query
ledger** split into guest and authenticated-user tables.

```
POST /guardrails/v1/input/check                 # scan a query before retrieval/generation
POST /guardrails/v1/output/check                # scan an answer before returning it
GET  /guardrails/v1/queries/{userType}/{sessionId}
GET  /health
```

`input/check` body: `{ text, sessionId, queryId?, userType: GUEST|AUTH, userId?, framework?, store? }`
→ `{ queryId, allowed, action, sanitizedText, reasons[], engine }` where `action` ∈
`allow | redact | flag | block` (block ⇒ `allowed=false`).

## Layers (defense-in-depth)
- **Rules engine** (always on, dependency-free): prompt-injection markers, out-of-scope markers,
  PII redaction (email/phone/SSN/card), length cap.
- **Model layer** (`VKP_GUARDRAILS_ENGINE`):
  - `groq` — content safety via Groq **`openai/gpt-oss-safeguard-20b`** (free, no torch). Catches
    weapons/violence/illegal/etc.
  - `llmguard` — protectai **llm-guard** scanners (PromptInjection, Toxicity; heavier — `pip install llm-guard`).
  - `auto` — llm-guard if importable, else rules. `rules` — rules only.
- **Output checks**: citation validity, light groundedness (cites the provided sources?), code/markup
  leak, PII redaction.

## Query ledger (Postgres)
`user_queries_guest` and `user_queries_auth_user` (the latter adds `user_id`), keyed by `query_id`:
input check inserts the row, output check updates it — recording `input_action/reasons` and
`output_action/reasons` per query + session.

## Run (localhost, :8091)
```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
VKP_GUARDRAILS_ENGINE=groq GROQ_API_KEY=$GROQ_API_KEY ./scripts/run.sh
```
Env: `VKP_PG_*` (default localhost vkp/vkp/vkp), `VKP_GUARDRAILS_ENGINE`, `VKP_GUARDRAILS_MAX_CHARS`,
`VKP_GROQ_GUARD_MODEL`. Called by **vehicle-explore-service** around each search.
