# AGENTS.md

Guidance for Codex (and other coding agents) when working in this repository. This mirrors the
conventions in [`CLAUDE.md`](CLAUDE.md); keep the two in sync when the architecture changes.

## Project status

This is **no longer greenfield — the platform is substantially built and runs end to end.** Treat the
`README.md` as the *business + architecture narrative* (strategic, not a code map) and this file as the
*as-built engineering guide*. What exists today:

- **Portals (Angular 19 + PrimeNG):** Admin (`:4200`), Vehicle Search (`:4201`), and a
  Context-Engineering workbench (`:4202`), reaching the backend through a dev proxy (`proxy.conf.json`).
- **Middleware:** multiple Spring Boot (Java 21) services (`:8081`–`:8088`, `:8094`) and Python /
  FastAPI services (`:8090`–`:8093`), plus the Airflow **DAG workflows** under
  `Middleware/Workflows/AirflowDAGS/`.
- **A complete agentic-pattern matrix** in `Middleware/agent-patterns-service/` (`:8094`): **10 agent
  patterns × 8 frameworks × 5 vehicle use cases — every cell verified live** (see that service's
  `Development_Tracker.md`).
- **Pipeline verified live:** Companies → Discovery → Ingestion → Indexing, plus guardrails, session
  security, request telemetry, and an AWS deploy path.

When asked to implement something, **match the existing as-built conventions below** (clone a reference
service) rather than scaffolding from the README's older prose.

## What VKP is

Vehicle Knowledge Platform (VKP) is an enterprise platform for discovering, crawling, extracting,
embedding, and semantically searching vehicle-related content (websites, blogs, docs, brochures, PDFs,
images, videos, social media). It pairs **Apache Airflow** (orchestration) with **LangGraph** and other
agent frameworks (ingestion + search), stores operational data in **MongoDB / Postgres**, and indexes
embeddings into one or more configurable **vector stores**.

Top-level folders are **PascalCase**: `Portals/` (Angular UIs) and `Middleware/` (all backend), plus
`DevOps/` for localhost/ops tooling, `Infra/` for the cloud deploy path, and a root `package.json` as
the operations entrypoint. (Browse the tree for the exact layout — it is not duplicated here.)

## Operations (root package.json)

The root `package.json` is **not an app package** — it is the operations entrypoint. All ops commands
are `npm run localhost:*` and delegate to scripts under `DevOps/Localhost/`:

| Command | Does |
|---|---|
| `localhost:containers:start-all` / `stop-all` / `status-all` | MongoDB + Postgres + Airflow compose |
| `localhost:services:java:start-all` / `stop-all` / `status-all` | all Spring Boot services under `Middleware/` |
| `localhost:services:python:start-all` / `stop-all` / `status-all` | same for Python (FastAPI/Flask) services |
| `localhost:services:start-all` / `stop-all` / `status-all` | both java + python |
| `localhost:portals:start-all` / `stop-all` | the Angular portals (4200/4201/4202) |
| `localhost:start-all` / `stop-all` / `status-all` | containers + services + portals |

Service runner scripts discover services by scanning `Middleware/` (Maven `pom.xml` for Java;
`requirements.txt`/`pyproject.toml` + `main.py` for Python), background each, and track pids/logs in
`DevOps/Localhost/.run/`.

**Docker images are reused, not redefined** — compose files pin images already on the machine
(`pgvector/pgvector:pg16`, `apache/airflow:2.10.0-python3.12`, `postgres:16`,
`mongodb/mongodb-atlas-local`). If you add infra, prefer an image already present (`docker images`).

## Spring Boot service conventions

> Reference implementations (built, runnable — clone their structure):
> - **`Middleware/company-service/`** — admin-facing CRUD (Company + Company Resource). The canonical
>   multi-module + DTO/Ctx + versioned-CRUD example.
> - **`Middleware/user-service/`** — customer-facing auth (signup/signin/reset/profile) over
>   `customer_users`; BCrypt + JWT (jjwt); shows the customer audience + non-CRUD operation groups.
> - **`Middleware/airflow-adapter-service/`** — the single gateway every service uses to invoke Apache
>   Airflow (trigger/status/tasks/retry/cancel). Stateless, calls Airflow's REST API via `RestClient`;
>   audience `internal`, port 8083. **No other service may call Airflow directly.**
> - **`Middleware/data-collection-service/`** — admin control plane for link discovery (port 8084).
>   Records the `company_resource_graph` root, then triggers `vkp_discover_resources` **through
>   airflow-adapter-service**. The DAG crawls the seed, extracts links, and calls back to persist them.
> - **`Middleware/ingestion-service/`** — admin control plane for content ingestion (port 8085).
>   Triggers `vkp_process_resources`; the DAG fetches discovered links, extracts title + clean text
>   (+ sha256), and calls back to persist into `company_resource_content`.
> - **`Middleware/indexing-service/`** — indexing control plane (port 8086) + a horizontally scalable
>   `wfs-java` executor module (port 8087). Routes a triggered run by `wf_type`: `AIRFLOW` → adapter→DAG
>   or `SPRING_AI` → `wfs-java`; dedup ledger on (company, workflow, formula).
> - **`Middleware/vector-config-service/`** — config-driven vector-store selection (port 8088, rule #3).
> - **`Middleware/agent-patterns-service/`** — the agentic-pattern lab (port 8094, FastAPI): every agent
>   pattern in every framework, selectable by use case via `POST /agent-patterns/{pattern}/{framework}/run`
>   with an optional `useCase`. Each pattern's use-case behaviour lives in a shared
>   `app/patterns/<pattern>/_base.py` catalog consumed by all framework cells. See its
>   `Development_Tracker.md` for the full matrix.
>
> Real DAGs live under `Middleware/Workflows/AirflowDAGS/Vehicles/`. Pattern to repeat: a **Java
> service** owns the data model + triggers via the adapter; the **Python DAG** does the work and calls
> back to persist. The **snapshot crawl** (`Crawl/vkp_crawl_company_snapshot.py`) does a real
> Playwright/Chromium recursive crawl writing a filesystem snapshot (pluggable `storage_backend`).

Every Spring Boot microservice is a **multi-module Maven project**: `api` (controllers + the
`@SpringBootApplication` entrypoint), `service` (business logic), `dao` (persistence),
`common` (shared DTOs/Ctx/enums/constants), `utils` (cross-cutting helpers).

**Naming:**
- Folder + parent artifact: `<domain>-service`. Modules: `<domain>-{common,utils,dao,service-core,api}`.
- Maven `groupId` + Java base package: **`com.jk.labs.vkp.<domain>`** with layers `.api/.service/.dao/.common/.utils`.
- **Class names use a short abbreviation of the domain noun** (e.g. `Comp` not `Company`): `CompDTO`,
  `CompResourceDTO`, `CreateCompReqDTO`, `CompEntity`, `CompService`, `CompController`.
- **Field / JSON / DB-column names stay descriptive** (`companyId`, table `companies`) — only *class*
  names are abbreviated.

**Bootable module = `api`** — run `mvn -pl api -am spring-boot:run` from the service root; fat jar is
`api/target/<domain>-service.jar`.

**Versioned API routes (mandatory):** `/<audience>/<domain>/service/v<major>/<group>/<resource>` where
`<audience>` is `admin` or `customer`. Define prefixes as constants in `common` and reference them from
`@RequestMapping`. The `GlobalExceptionHandler` maps `NoResourceFoundException` → 404.

**Cross-cutting standards every microservice MUST include:**
- **Swagger/OpenAPI** (`springdoc-openapi-starter-webmvc-ui`) → `/swagger-ui.html`, `/v3/api-docs`.
- **Metrics** (Actuator + `micrometer-registry-prometheus`) → `/actuator/prometheus`; health `/actuator/health`.
- **Logging** via SLF4J — Lombok `@Slf4j`; never call a concrete logger directly.
- Lombok throughout (`@Data`/`@Builder`/`@Getter`/`@Setter`/`@RequiredArgsConstructor`).

**DTO + Context method-argument pattern (mandatory):** every method from controller to DAO takes a
**single context object**, never positional arguments. Per use case define `<UseCase>ReqDTO`,
`<UseCase>RespDTO`, and `<UseCase>Ctx` (holding both). The same `Ctx` instance is threaded api → service
→ dao; each layer reads its `ReqDTO` and populates its `RespDTO`.

**Persistence:** Spring Data **JPA** with profile-driven datasources — `h2` (default, in-memory),
`postgres` (pgVector-capable), `mongodb`. Select via Spring profile; do not hardcode a datasource.

## Technology choices

- **Frontend:** **Angular** (3 portals — Admin, Vehicle Search, Context-Engineering).
- **Spring Boot services** (Java 21): company, user, data-collection, ingestion, airflow-adapter,
  indexing, vector-config, agent-patterns.
- **Python services** (FastAPI): vehicle-explore, guardrails, agentic, context-engine.
- **Orchestration:** Apache Airflow + LangGraph (and 7 other agent frameworks in agent-patterns-service).
- **AI:** OpenAI / Azure OpenAI / Groq.
- **Vector stores** (config-driven, none hardcoded): MongoDB Atlas Vector Search, ChromaDB, pgVector,
  Weaviate, Pinecone.
- **Infra:** Docker, Kubernetes, Terraform / AWS CloudFormation. **Monitoring:** Prometheus, Grafana, OpenTelemetry.

## Key architectural rules

These are load-bearing constraints — preserve them in any implementation:

0. **`Portals/` (Angular) and `Middleware/` are the two domain folders;** `DevOps/` + root
   `package.json` are the ops layer. Middleware mixes Spring Boot + Python services *and* the DAG
   workflows, grouped categorically by data-management use case.
1. **All Airflow access goes through `airflow-adapter-service`.** No portal or business service calls
   Airflow directly.
2. **Data Collection vs Ingestion are distinct.** `data-collection-service` *discovers links only*
   (→ `company_resource_graph`); `ingestion-service` does the crawling + content extraction
   (→ `company_resource_content`) and triggers indexing.
3. **Vector store selection is configuration-driven** (`company_resource_vector_config`); never
   hardcode a store choice.
4. **AI framework is part of the URL** for search routing:
   `POST /api/vehicle-explore/{frameworkName}/search` (and, in the lab,
   `POST /agent-patterns/{pattern}/{framework}/run`).

## Core flows

- **Discovery:** Admin Portal → Data Collection Service → Airflow Adapter → Airflow
  (`vkp_discover_resources`) → updates `company_resource_graph`.
- **Ingestion:** Admin Portal → Ingestion Service → Airflow Adapter → Airflow
  (`vkp_process_resources` → `vkp_extract_content`) → `company_resource_content` →
  `vkp_langgraph_index_content` → chunk/embed/route → configured vector stores.
- **Search:** Vehicle Search Portal → User Management → Vehicle Explore Service → framework router →
  vector search → LLM response → result cards (answer, snippets, images, source links, citations).

## Working in this repo

- **Ops commands:** root `package.json` → `npm run localhost:*`. Java services build/run via Maven;
  Python services run from their own `.venv` (each FastAPI service manages its own).
- When implementing a Spring Boot service, **clone a reference service** and follow the multi-module +
  `ReqDTO`/`RespDTO`/`Ctx` + JPA-profile conventions above.
- When implementing a Python service, default to FastAPI under `Middleware/<service>/` with an
  `app/main.py` (or `main.py`) `app` so the runner script finds it.
- **Always record installs** — add any installed package to the relevant `requirements.txt` / `pom.xml`
  in the same change.
- New DAGs go under `Middleware/Workflows/AirflowDAGS/<Domain>/<UseCase>/`.
- Reuse Docker images already on the machine; don't introduce new infra images casually.
- Keep the `README.md`, `CLAUDE.md`, and this file in sync when the architecture changes.
- Conventional/working branch is `main`; commit/push only when asked. Commit as
  `javakishore-veleti <javakishore@gmail.com>` (the repo identity).
