# CEF Portal

**cef-portal/** — the Angular portal for the Context Engineering Framework (Angular 19 standalone
components, like the VKP admin-portal but lean: no PrimeNG). It consolidates both CEF surfaces as routes:

- **Chat** (`/chat`) — customer **context-aware vehicle chat** over the context-engine orchestrator
  (proxied `/context-engine` → `:8093`). The session persists, so you can watch the **Context
  Evolution loop** carry memory across turns; each reply shows the context stats
  (retrieved/used/memory turns/strategies/model/latency).
- **Admin** (`/admin`) — the CEF **context-strategy table** + **eval harness** (proxied
  `/admin/context-engine` → context-admin `:8094`), scorecarding groundedness.

## Run
```bash
cd cef-portal
npm start            # ng serve with proxy.conf.json
```
Requires the CEF services up: `context-engine-service` (:8093) and `context-admin-service` (:8094),
plus Postgres (retrieval). The dev proxy reaches both — no CORS needed.

> Replaces the earlier lightweight static SPAs (cef-search-portal / cef-admin-portal), now upgraded
> to this Angular app per the VKP portal convention. The Chat and Admin areas can be split into two
> separate Angular apps later if a hard admin/customer boundary is wanted.
