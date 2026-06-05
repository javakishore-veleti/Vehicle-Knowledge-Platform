# CEF Portals

Two lightweight **static** portals for the Context Engineering Framework — separate from the VKP
Angular admin/customer portals, matching the "independent sub-project" intent.

- **cef-search-portal/** — customer **context-aware vehicle chat**. Calls the context-engine
  orchestrator (`:8093`); each turn shows the context stats (retrieved/used/memory turns/strategies),
  and the session persists so you can watch the **Context Evolution loop** carry memory across turns.
- **cef-admin-portal/** — **strategy config** table + **eval harness**. Calls context-admin (`:8094`):
  lists the CEF context strategies and runs a golden query through the orchestrator, scorecarding
  groundedness (citations/sources/latency).

## Run
```bash
bash serve.sh          # customer chat -> http://localhost:5173 ; admin -> http://localhost:5174
```
Requires the CEF services up: `context-engine-service` (:8093) and `context-admin-service` (:8094),
plus Postgres (retrieval). The services have dev CORS enabled so the static pages can call them.

Lightweight by design; upgradeable to full Angular apps to match the VKP portals if desired.
