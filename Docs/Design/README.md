# Design diagrams

**`vkp-architecture.drawio`** — multi-tab architecture diagram for VKP. Open it with:
- [diagrams.net](https://app.diagrams.net) (File → Open), or
- the VS Code **Draw.io Integration** extension (`hediet.vscode-drawio`).

Tabs:

1. **System Overview** — portals → middleware → data stores + Airflow + external AI vendors.
2. **Middleware Services** — every Spring Boot (Java) and Python service with its port.
3. **Database & Schema model** — one `postgres` database with per-service `vkp_*` schemas + the shared `vkp_vectors` schema.
4. **Search Flow** — the vehicle-search request pipeline recorded in `vkp_explore.veh_search_request_log`.
5. **CEF Pipeline** — the Context Engineering Framework orchestrate pipeline (permission → retrieve → memory → assemble → reason → evolve).
6. **AWS Deployment** — the CloudFormation + categorized `AWS_001..901` GitHub workflows (infra / build / workloads / orchestrators).

The diagram is a source-of-truth design artifact; keep it in sync with `README.md` and `CLAUDE.md` when the architecture changes.
