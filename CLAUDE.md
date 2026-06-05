# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project status

This is a **greenfield repository**. As of now it contains only `README.md`, `LICENSE`,
and `.gitignore` — there is no application code, build system, or tests yet. The
`README.md` is a detailed **architecture and design specification**, not documentation of
existing code. Treat the structures, services, and APIs below as the *intended* design to
be built, not as code that already exists. When asked to implement something, scaffold it
to match this spec.

## What VKP is

Vehicle Knowledge Platform (VKP) is a planned enterprise platform for discovering,
crawling, extracting, embedding, and semantically searching vehicle-related content
(websites, blogs, docs, brochures, PDFs, images, videos, social media). It pairs **Apache
Airflow** (orchestration) with **LangGraph** (ingestion + search agents), stores
operational data in **MongoDB**, and indexes embeddings into one or more configurable
**vector stores**.

The system uses **PascalCase top-level folders**: `Portals/` (Angular UIs) and
`Middleware/` (all backend), plus `DevOps/` for localhost/ops tooling, `Infra/` for the
cloud/cluster deploy path (Dockerfiles + Kubernetes kustomize + Terraform), and a root
`package.json` as the operations entrypoint.

- **`Portals/`** — user-facing **Angular** UIs. Two or more portals (at minimum an Admin
  Portal and a Vehicle Search Portal; more may be added). **`Portals/admin-portal/`** is built
  (Angular 19 + **PrimeNG**, light theme, fixed top bar + contextual left sidebar): Companies
  CRUD/search and a Data Management section (Data Collection/Ingestion/Indexing → Overview +
  Workflows). It uses a dev proxy (`proxy.conf.json`) to reach the Spring services — no CORS
  config needed. Run: `npm run localhost:portals:admin:start` (→ `:4200`).
- **`Middleware/`** — everything backend. Holds **both** Spring Boot (Java 21) **and**
  Python (Flask / FastAPI) microservices, **and** the Airflow **DAG workflows** under
  `Middleware/Workflows/AirflowDAGS/`. DAGs are organized **categorically by functionality /
  data-management use case** (e.g. `Vehicles/DataCollection`, `Vehicles/Ingestion`), not as
  a flat `dags/` directory.

## Repository layout

This is the actual scaffolded layout (folders not yet created are marked *(planned)*):

```text
package.json                      # ROOT ops entrypoint — npm run localhost:* (see Operations)
DevOps/
  Localhost/
    docker-all-up.sh  docker-all-down.sh  docker-all-status.sh
    MongoDB/docker-compose.yaml       # mongodb-atlas-local (vector search)
    Postgres/docker-compose.yaml      # pgvector/pgvector:pg16 + initdb/ (CREATE EXTENSION vector)
    Airflow/docker-compose.yaml       # apache/airflow:2.10.0 (LocalExecutor) + postgres:16 meta
    Services/                         # java-* and python-* start/stop/status scripts
    .run/                             # (gitignored) pidfiles + logs for local services

Portals/                          # (planned) Angular UIs (2+ portals)
  admin-portal/  vehicle-search-portal/

Middleware/                       # Spring Boot + Python services AND DAG workflows
  # --- Spring Boot / Java 21 services (each a multi-module Maven project) ---
  admin-service/  customer-management-service/  user-management-service/
  data-collection-service/  ingestion-service/  airflow-adapter-service/
  vector-config-service/  common/                       # (all planned)
  # --- Python services (planned) ---
  vehicle-explore-service/        # FastAPI preferred — AI search (LangGraph/CrewAI)
  # --- DAG workflows, grouped categorically (scaffolded) ---
  Workflows/AirflowDAGS/
    Vehicles/
      DataCollection/             # crawl LINKS ONLY; update Company Resource graph table
      Ingestion/                  # iterate links, fetch ACTUAL content, store to FS/S3/blob
      Indexing/  VectorDbs/       # (add as needed)
```

Named DAGs from the README (`vkp_discover_resources`, `vkp_process_resources`,
`vkp_extract_content`, `vkp_langgraph_index_content`, `vkp_refresh_content`) live under the
matching category folder rather than a flat list. The README itself contains older sketches
(flat `airflow/dags/`, a `services/` variant, React/Next.js) — the layout above supersedes them.

## Operations (root package.json)

The root `package.json` is **not an app package** — it is the operations entrypoint. All
ops commands are `npm run localhost:*` and delegate to scripts under `DevOps/Localhost/`:

| Command | Does |
|---|---|
| `localhost:containers:start-all` / `stop-all` / `status-all` | `DevOps/Localhost/docker-all-{up,down,status}.sh` → MongoDB + Postgres + Airflow compose |
| `localhost:services:java:start-all` / `stop-all` / `status-all` | start/stop/status all Spring Boot services found under `Middleware/` |
| `localhost:services:python:start-all` / `stop-all` / `status-all` | same for Python (FastAPI/Flask) services |
| `localhost:services:start-all` / `stop-all` / `status-all` | runs **both** java + python variants |

Service runner scripts discover services by scanning `Middleware/` (Maven `pom.xml` for
Java; `requirements.txt`/`pyproject.toml` + `main.py` for Python), background each, and
track pids/logs in `DevOps/Localhost/.run/`. They no-op gracefully until services exist.

**Docker images are reused, not redefined** — the compose files pin images already on the
machine: `pgvector/pgvector:pg16` (Postgres+pgVector), `apache/airflow:2.10.0-python3.12`,
`postgres:16` (Airflow metadata). MongoDB uses `mongodb/mongodb-atlas-local` (no local Mongo
image existed; it is pulled on first `up`). If you add infra, prefer an image already
present (`docker images`) over introducing a new one.

## Spring Boot service conventions

> Reference implementations (both fully built, tested on H2, runnable — clone their structure):
> - **`Middleware/company-service/`** — admin-facing CRUD (Company + Company Resource). The
>   canonical example of the multi-module + DTO/Ctx + versioned-CRUD pattern. ("Company" is
>   the README data-model term; the README's "Customer Management Service" is the same admin
>   role, reconciled to Company here.)
> - **`Middleware/user-service/`** — customer-facing auth (signup, signin, forgot/reset
>   password, profile) over `customer_users`. Adds BCrypt password hashing + JWT (jjwt), and
>   shows the customer audience + non-CRUD operation groups (`/auth`, `/profile`).
> - **`Middleware/airflow-adapter-service/`** — the single gateway every service uses to
>   invoke Apache Airflow (trigger/status/tasks/retry/cancel). Stateless (no `dao`), calls
>   Airflow's REST API via Spring `RestClient`; routes `/internal/airflow/service/v1/...`
>   (audience `internal`), port 8083. **No other service may call Airflow directly.**
>   Requires Airflow REST basic-auth — our `DevOps/Localhost/Airflow` compose enables it
>   (`AIRFLOW__API__AUTH_BACKENDS=...basic_auth,...session`, admin/admin) and unpauses DAGs
>   at creation (`DAGS_ARE_PAUSED_AT_CREATION=false`).
> - **`Middleware/data-collection-service/`** — admin control plane for link discovery
>   (port 8084). Records the `company_resource_graph` root, then triggers the
>   `vkp_discover_resources` DAG **through airflow-adapter-service** (a `RestClient` to the
>   adapter — never Airflow directly). The DAG really crawls the seed, extracts links, and
>   calls back (`POST …/graph/record`) to persist them.
> - **`Middleware/ingestion-service/`** — admin control plane for content ingestion
>   (port 8085). Triggers `vkp_process_resources`, whose DAG fetches discovered links from
>   data-collection, crawls each, extracts title + clean text (+ sha256), and calls back
>   (`POST …/content/record`) to persist into `company_resource_content`. Same template.
> - **`Middleware/indexing-service/`** — indexing **control plane** (port 8086) + a second
>   bootable module **`wfs-java`** (`indexing-service-wfs-java`, port 8087, horizontally
>   scalable). Liquibase metadata: `indexing_workflow` (registry, 10k+), `index_formula`,
>   `provider_credentials`, `resource_graph_index_log` (the dedup/restart ledger). The control
>   plane never embeds — it **routes** a triggered run by the workflow's `wf_type`: `AIRFLOW`
>   → adapter→DAG, or `SPRING_AI` → `wfs-java` `POST /wfs/{id}/execute` (async); executors
>   report status back via `POST …/index-logs/{id}/callback`. Dedup on
>   (company, workflow, formula). **Phase 1 done** (routing + dedup + ledger, execution
>   stubbed); Phase 2 wires Spring AI `TransformersEmbeddingModel`→`PgVectorStore` + a Python
>   embed DAG. (Note: `java-start-all.sh` starts only the `api` module; run `wfs-java`'s jar
>   separately.)
>
> Real DAGs live under `Middleware/Workflows/AirflowDAGS/Vehicles/` —
> `DataCollection/vkp_discover_resources.py` and `Ingestion/vkp_process_resources.py`
> (Python, stdlib only). **Pipeline verified live: Companies → Discovery → Ingestion.**
> Pattern to repeat: a **Java service** owns the data model + triggers via the adapter; the
> **Python DAG** does the actual work and calls back to persist.
>
> **Snapshot crawl** — `Crawl/vkp_crawl_company_snapshot.py` does a real **Playwright/Chromium**
> recursive crawl (pulls a company's root links from company-service) and writes a **filesystem
> snapshot** (NOT Postgres) under `~/runtime_data/ai_projects/Vehicle-Knowledge-Platform/
> Crawling-Snapshot/<Company>/`: `crawl-NNNNN.json` (≤250 page elements each), `images/<uuid>.<ext>`,
> and `__COMPLETED__/manifest.json` (its presence makes re-runs skip — so dropping Postgres never
> forces a re-crawl). Storage is pluggable via `conf.storage_backend` (`local` now; `s3`/`azure`/`gcs`
> stubs for cloud). Requires the **custom Airflow image** (`DevOps/Localhost/Airflow/Dockerfile`:
> Airflow + Playwright + Chromium) and the snapshot host-dir volume mount (both in the Airflow compose).

Every Spring Boot microservice is a **multi-module Maven project** with these modules:

- **api** — controllers / REST layer **+ the Spring Boot `@SpringBootApplication` entrypoint**
- **service** — business logic
- **dao** — persistence (Spring Data JPA repositories / Mongo repositories)
- **common** — shared domain types, DTOs, Ctx, enums, constants
- **utils** — cross-cutting helpers

**Naming:**
- Folder + parent artifact: `<domain>-service` (e.g. `company-service`). Module artifacts:
  `<domain>-common`, `<domain>-utils`, `<domain>-dao`, `<domain>-service-core`, `<domain>-api`.
- Maven `groupId` + Java base package: **`com.jk.labs.vkp.<domain>`** (`jk` = javakishore,
  `labs` = labs). Layers: `.api`, `.service`, `.dao`, `.common`, `.utils`.
- **Class names use a short abbreviation of the domain noun** to avoid long names — e.g.
  `Comp` not `Company`: `CompDTO`, `CompResourceDTO`, `CreateCompReqDTO`, `CreateCompCtx`,
  `CompEntity`, `CompRepository`, `CompService`, `CompController`, `CompServiceApplication`.
- **Field / JSON / DB-column names stay descriptive** (`companyId`, `company_resource_id`,
  table `companies`) to match the README data model — only *class* names are abbreviated.

**Bootable module = `api`.** Run with `mvn -pl api -am spring-boot:run` from the service root
(the `java-start-all.sh` runner does this automatically). The fat jar is `api/target/<domain>-service.jar`.

**Versioned API routes (mandatory):** `/<audience>/<domain>/service/v<major>/<group>/<resource>`
where `<audience>` is `admin` (operator-facing) or `customer` (end-user-facing). Examples:
`/admin/company/service/v1/crud/companies/{companyId}/resources` (company-service) and
`/customer/user/service/v1/auth/signin` + `/customer/user/service/v1/profile/{userId}`
(user-service). Define the prefixes as constants in `common` (`ApiRoutes.API_BASE` → group
consts like `.CRUD` / `.AUTH` / `.PROFILE`) and reference them from `@RequestMapping`, so a
version bump or new operation group is a one-line change. The `GlobalExceptionHandler` maps
`NoResourceFoundException` → 404 so unmapped/old paths return 404 (not 500).

**Cross-cutting standards every microservice MUST include:**
- **Swagger UI / OpenAPI** via `springdoc-openapi-starter-webmvc-ui` → UI at `/swagger-ui.html`,
  spec at `/v3/api-docs`. Add an `OpenApiConfig` `@Bean` for title/version.
- **Metrics** via Spring Boot Actuator + `micrometer-registry-prometheus` → scrape at
  `/actuator/prometheus` (tagged `application=<name>`); health at `/actuator/health`.
- **Logging** via **SLF4J** — use Lombok `@Slf4j` (over Spring Boot's Logback). Never call a
  concrete logger directly.
- Lombok throughout: `@Data`/`@Builder`/`@NoArgsConstructor`/`@AllArgsConstructor` on DTOs,
  `@Getter`/`@Setter` on entities, `@RequiredArgsConstructor` for constructor injection.

**DTO + Context method-argument pattern (mandatory):** every method from controller down to
DAO takes a **single context object**, never independent/positional arguments. For each use
case define:

- `<UseCase>ReqDTO` — request fields
- `<UseCase>RespDTO` — response fields
- `<UseCase>Ctx` — a context holding **both** a `ReqDTO` and a `RespDTO` member

The same `<UseCase>Ctx` instance is threaded through every layer (api → service → dao); each
layer reads from its `ReqDTO` and populates its `RespDTO`. No method declares standalone
parameters.

**Persistence:** Spring Data **JPA** with profile-driven datasources:

- **`h2`** — default (in-memory) for local dev / tests
- **`postgres`** — Postgres (pgVector-capable) profile
- **`mongodb`** — MongoDB profile

Select via Spring profile; do not hardcode a datasource.

## Technology choices (from the spec)

- **Frontend**: **Angular** (the `portals/` folder; 2+ portals). *(The README's prose still
  says React/Next.js — Angular is the decided direction; prefer it.)*
- **Spring Boot services** (Java 21, MongoDB): admin, customer-management, user-management,
  data-collection, ingestion, airflow-adapter, vector-config
- **Python AI service**: `vehicle-explore-service` — **FastAPI preferred** (Flask only for
  simple prototypes), LangGraph, CrewAI, LLM + vector DB SDKs
- **Orchestration**: Apache Airflow + LangGraph
- **AI**: OpenAI / Azure OpenAI
- **Vector stores** (config-driven, none hardcoded): MongoDB Atlas Vector Search, ChromaDB,
  pgVector, Weaviate, Pinecone
- **Infra**: Docker, Kubernetes, Terraform — **Monitoring**: Prometheus, Grafana, OpenTelemetry

## Key architectural rules

These are load-bearing design constraints — preserve them in any implementation:

0. **`Portals/` (Angular) and `Middleware/` are the two domain folders;** `DevOps/` + root
   `package.json` are the ops layer. Middleware mixes Spring Boot and Python services *and*
   the DAG workflows (`Middleware/Workflows/AirflowDAGS/`), grouped categorically by
   data-management use case (Vehicles/DataCollection, Vehicles/Ingestion, …).
1. **All Airflow access goes through `airflow-adapter-service`.** No portal or business
   service calls Airflow directly. The adapter triggers DAGs, queries run/task status,
   retries, cancels, and normalizes responses.
2. **Data Collection vs Ingestion are distinct.** `data-collection-service` *discovers links
   only* (sitemaps, page links, image/document URLs → `company_resource_graph`). It does NOT
   extract page content. `ingestion-service` does the actual crawling, content extraction
   (→ `company_resource_content`), and triggers indexing.
3. **Vector store selection is configuration-driven.** A resource may index into one or many
   stores via `company_resource_vector_config`; never hardcode a store choice.
4. **AI framework is part of the URL** for search routing:
   `POST /api/vehicle-explore/{frameworkName}/search` (e.g. `langgraph`, `crewai`,
   `llamaindex`, `haystack`) so requests route dynamically to different implementations.

## Data model (MongoDB collections + owning service)

| Collection | Owning service |
|---|---|
| `companies` | Admin Service |
| `company_resources` | Admin / Customer Management Service |
| `company_resource_graph` | Data Collection Service |
| `company_resource_content` | Ingestion Service |
| `company_resource_vector_config` | Vector Config Service |
| `company_resource_index_status` | Ingestion / LangGraph Indexing |
| `workflow_runs`, `workflow_run_steps` | Airflow Adapter Service |
| `customer_users` | User Management Service |
| `search_history`, `search_feedback` | Vehicle Explore Service |

Common entity conventions: UUID-string ids, `status` fields, and audit columns
(`created_dt`, `updated_dt`, `created_by`, `updated_by`). Index status flows through
`PENDING → IN_PROGRESS → COMPLETED / FAILED / SKIPPED / DEAD_LETTER`. See README "Data
Architecture" for full field-level schemas before creating models.

## Core flows

- **Discovery**: Admin Portal → Data Collection Service → Airflow Adapter → Airflow
  (`vkp_discover_resources`) → updates `company_resource_graph`.
- **Ingestion**: Admin Portal → Ingestion Service → Airflow Adapter → Airflow
  (`vkp_process_resources` → `vkp_extract_content`) → `company_resource_content` →
  `vkp_langgraph_index_content` → LangGraph chunk/embed/route → configured vector stores.
- **Search**: Vehicle Search Portal → User Management Service → Vehicle Explore Service →
  framework router → vector search → LLM response → result cards (answer, snippets, images,
  source links, citations, scores).

## Working in this repo

- **Ops commands exist** (root `package.json` → `npm run localhost:*`); there is **no
  service build/test command yet** because no services exist. Don't invent service tooling;
  scaffold per the conventions above and say so.
- When implementing a Spring Boot service, follow the multi-module + `ReqDTO`/`RespDTO`/`Ctx`
  + JPA-profile conventions above and the example APIs in the README.
- When implementing a Python service, default to FastAPI under `Middleware/<service>/` with
  an `app/main.py` (or `main.py`) `app` so the runner script finds it.
- New DAGs go under `Middleware/Workflows/AirflowDAGS/<Domain>/<UseCase>/`, matching the
  data-management category (e.g. DataCollection = links only; Ingestion = fetch content).
- Reuse Docker images already on the machine; don't introduce new infra images casually.
- Keep the README and this file in sync if the architecture changes.
- Conventional/working branch is `main`; commit/push only when asked.
