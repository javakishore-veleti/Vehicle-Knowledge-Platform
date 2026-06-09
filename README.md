# Vehicle Knowledge Platform (VKP)

## Overview

Vehicle Knowledge Platform (VKP) is an enterprise-grade platform for discovering, crawling, processing, indexing, embedding, and semantically searching vehicle-related digital content across multiple online resources.

The platform combines:

- Apache Airflow for workflow orchestration
- LangGraph for intelligent ingestion and search workflows
- LLMs for content understanding and response generation
- Multiple configurable vector databases
- MongoDB for operational and metadata storage
- Customer-facing AI-powered search experiences

The platform supports intelligent ingestion of publicly available vehicle-related information including:

- Vehicle websites
- Product and specification pages
- Blogs and articles
- Documentation
- Brochures
- Images
- PDFs
- Videos
- Social media resources

---

## Table of Contents

- [Quick Start](#quick-start)
- [Architecture diagram](#architecture-diagram)
- [Database & schema model](#database--schema-model)
- [Platform Vision](#platform-vision)
- [Major Components](#major-components)
- [High-Level Architecture](#high-level-architecture)
- [Data Architecture](#data-architecture)
- [Middleware Services](#middleware-services)
- [Technology Stack](#technology-stack)

> Everything below the Quick Start is the **design specification**. See `CLAUDE.md` for the as-built
> layout and `Docs/Design/vkp-architecture.drawio` for the architecture diagram.

## Quick Start

### Prerequisites
- **Docker Desktop** — Postgres + Mongo (and Airflow when you need DAGs)
- **Java 21 + Maven** — the Spring Boot services
- **Node + npm** — the Angular portals and the `npm run localhost:*` ops scripts
- **Python 3.12** — the FastAPI services (each creates its own `.venv` on first run)

### One command (everything)
```bash
npm install                    # once, in the repo root
npm run localhost:start-all    # containers + middleware + portals
npm run localhost:status-all   # see what is up
```
First run is slow (Python venvs, npm installs, Maven downloads). Then open:

| Portal | URL |
|---|---|
| Admin Portal | http://localhost:4200 |
| Vehicle Search | http://localhost:4201 |
| CEF Portal | http://localhost:4202 |

### Granular (recommended when low on memory/disk)
```bash
npm run localhost:containers:start-all   # Postgres + Mongo (+ Airflow; observability disabled)
npm run localhost:services:start-all     # Java (8081–8088, 8094) + Python (8090–8093)
npm run localhost:portals:start-all      # 4200 / 4201 / 4202
```

### Stop / restart / status
| Command | Does |
|---|---|
| `npm run localhost:stop-all` | portals + services + containers |
| `npm run localhost:restart-all` | restart middleware + portals (leaves containers up) |
| `npm run localhost:services:restart-all` | restart just the services (after a code change) |
| `npm run localhost:containers:airflow:stop` | shut down Airflow on its own (heaviest stack) |
| `npm run localhost:status-all` | status of containers + services + portals |

Observability (Jaeger/Prometheus/Grafana) is disabled in the container scripts by default to save
memory/disk — re-enable by uncommenting the `STACKS` line in `DevOps/Localhost/docker-all-*.sh`.

### Good to know
- **Java services run on in-memory H2 by default** — they start without Postgres. (The `postgres`
  profile + `vkp_*` schemas only apply to the cloud/deploy path.)
- **Python services need the databases**: explore `:8090`, guardrails `:8091`, agentic `:8092`,
  context-engine `:8093` use Postgres (the `postgres` database + `vkp_*` schemas, auto-created) and
  Mongo — start the containers first.
- **The vector table starts empty**, so search/chat return no sources until content is indexed. Seed one:
  ```bash
  curl -s -X POST http://localhost:8090/api/vehicle-explore/langgraph/index \
    -H 'Content-Type: application/json' \
    -d '{"content":"The Toyota RAV4 Hybrid is an AWD hybrid SUV, ~39 MPG, around $31k.","sourceUrl":"https://toyota.com/rav4","companyId":"10000000-0000-4000-8000-000000000004"}'
  ```
  Then search “hybrid SUV”. Real data flows through Discovery → Ingestion → Indexing (Admin Portal + Airflow).
- **`indexing-wfs` (:8087)**: `java-start-all` starts only the indexing `api` module; run the wfs jar
  separately for the Spring-AI executor.
- Per-service logs live under `DevOps/Localhost/.run/{java,python,portal}-<name>.log`.

### Ports
- **Java** — company 8081 · user 8082 · airflow-adapter 8083 · data-collection 8084 · ingestion 8085 ·
  indexing 8086 · indexing-wfs 8087 · vector-config 8088 · context-admin 8094
- **Python** — vehicle-explore 8090 · guardrails 8091 · agentic 8092 · context-engine 8093

### Cloud (AWS)
Manual GitHub workflows provision EKS via CloudFormation — run `AWS_900_Run_All` (see
`Infra/cloudformation/README.md`). Architecture: `Docs/Design/vkp-architecture.drawio`.

## Architecture diagram

A multi-tab **draw.io** diagram lives at [`Docs/Design/vkp-architecture.drawio`](Docs/Design/vkp-architecture.drawio)
— open it at [diagrams.net](https://app.diagrams.net) or with the VS Code *Draw.io Integration* extension.
Tabs: **1. System Overview**, **2. Middleware Services**, **3. Database & Schema model**,
**4. Search Flow**, **5. CEF Pipeline**, **6. AWS Deployment**.

## Database & schema model

One Postgres **server** (Docker, `pgvector/pgvector:pg16`) → one **database named `postgres`** → the
codebase's logical DBs are **schemas** inside it (not separate databases), each `vkp_`-prefixed:
`vkp_company`, `vkp_user`, `vkp_data_collection`, `vkp_ingestion`, `vkp_indexing`, `vkp_vector_config`,
`vkp_guardrails`, `vkp_explore`, `vkp_cef`, plus a shared **`vkp_vectors`** schema for the embeddings
table (`vec_all_minilm_l6_v2`) read by indexing, explore and CEF. Services connect with
`search_path=<vkp_schema>,vkp_vectors,public`; see `DevOps/Localhost/Postgres/initdb/02-schemas.sql`.

---

# Platform Vision

VKP is not just a crawler.

VKP is a complete:

- Vehicle Knowledge Repository
- AI Search Platform
- Agentic Retrieval Platform
- Semantic Search Platform
- Multi-Vector Store Knowledge System

The architecture is designed to support:

- Resource discovery
- Resource graph generation
- Content extraction
- AI enrichment
- Embedding generation
- Multi-vector-store indexing
- Agentic search
- Customer-facing conversational experiences

---

# Major Components

## Admin Portal

Used by platform administrators and operators.

Capabilities:

- Company onboarding
- Resource registration
- Workflow execution
- Crawl monitoring
- Content review
- Retry failed resources
- Vector store configuration
- Search analytics
- Audit reporting

---

## Customer Portal

Used by end users.

Capabilities:

- Signup
- Signin
- Forgot Password
- User Profile
- Search History
- Saved Searches
- Agentic AI Search
- Semantic Search
- Hybrid Search
- AI-generated Answers
- Image-rich Results
- Source Links
- Citations

---

# Customer Search Experience

Users can ask:

- Show vehicles with advanced safety features
- Find content related to electric vehicles
- Compare vehicle technologies
- Find towing-related vehicle information
- Show brochures related to specific vehicle categories

Results may contain:

- AI summary
- Relevant content snippets
- Images
- Related documents
- PDF links
- Website links
- Source citations
- Confidence scores

---

# High-Level Architecture

```text
Customer Portal
       |
       v
Search API
       |
       v
LangGraph Search Agent
       |
       +--> Query Understanding
       +--> Query Rewriting
       +--> Metadata Filtering
       +--> Vector Search
       +--> Image Retrieval
       +--> Link Retrieval
       +--> LLM Response Generation
       |
       v
Search Results


Admin Portal
       |
       v
Apache Airflow
       |
       +----------------------------+
       |                            |
       v                            v

Resource Discovery          Resource Processing

       |                            |
       v                            v

MongoDB Operational Database

       |
       v

LangGraph Ingestion Workflow

       |
       +--> Chunk Content
       +--> Generate Embeddings
       +--> Route To Vector Stores

       |
       +--> MongoDB Vector Search
       +--> ChromaDB
       +--> pgVector
       +--> Weaviate
       +--> Pinecone
```

---

# Why Airflow + LangGraph

## Airflow Responsibilities

Airflow is responsible for:

- Scheduling
- Monitoring
- Retries
- Backfills
- Dependency management
- Workflow execution
- Admin-triggered jobs

Example DAGs:

```text
vkp_discover_resources
vkp_process_resources
vkp_extract_content
vkp_langgraph_index_content
vkp_refresh_content
```

## LangGraph Responsibilities

LangGraph is responsible for:

### Ingestion

- Chunking
- Metadata enrichment
- Embedding generation
- Conditional routing
- Multi-vector-store indexing
- Error handling

### Search

- Query understanding
- Query rewriting
- Retrieval
- Ranking
- Result generation
- Citation generation

---

# Data Architecture

## Company

| Field | Type |
|---------|---------|
| company_id | UUID String |
| name | VARCHAR(100) |
| description | VARCHAR(250) |
| status | VARCHAR(15) |
| created_dt | TIMESTAMP |
| updated_dt | TIMESTAMP |
| created_by | VARCHAR(50) |
| updated_by | VARCHAR(50) |

---

## Company Resource

| Field | Type |
|---------|---------|
| company_resource_id | UUID String |
| company_id | UUID String |
| resource_name | VARCHAR(150) |
| resource_link | VARCHAR(1000) |
| resource_type | VARCHAR(50) |
| status | VARCHAR(15) |
| created_dt | TIMESTAMP |
| updated_dt | TIMESTAMP |
| created_by | VARCHAR(50) |
| updated_by | VARCHAR(50) |

Examples:

- Website
- Blog
- Documentation
- Social Media
- PDF
- Video
- Image Repository

---

## Company Resource Graph

Stores discovered resources.

| Field | Type |
|---------|---------|
| resource_graph_id | UUID String |
| company_id | UUID String |
| company_resource_id | UUID String |
| parent_resource_graph_id | UUID String |
| resource_url | VARCHAR(1000) |
| resource_type | VARCHAR(50) |
| parent_resource_type | VARCHAR(50) |
| crawl_status | VARCHAR(30) |
| status | VARCHAR(15) |
| addl_data | JSON |
| created_dt | TIMESTAMP |
| updated_dt | TIMESTAMP |
| created_by | VARCHAR(50) |
| updated_by | VARCHAR(50) |

---

## Company Resource Content

Stores extracted content.

| Field | Type |
|---------|---------|
| content_id | UUID String |
| company_id | UUID String |
| company_resource_id | UUID String |
| resource_graph_id | UUID String |
| source_url | VARCHAR(1000) |
| title | VARCHAR(250) |
| description | TEXT |
| raw_text | TEXT |
| clean_text | TEXT |
| content_hash | VARCHAR(128) |
| embedding_status | VARCHAR(30) |
| crawl_status | VARCHAR(30) |
| addl_data | JSON |
| created_dt | TIMESTAMP |
| updated_dt | TIMESTAMP |
| created_by | VARCHAR(50) |
| updated_by | VARCHAR(50) |

---

## Company Resource Vector Configuration

Determines where content should be indexed.

| Field | Type |
|---------|---------|
| vector_config_id | UUID String |
| company_id | UUID String |
| company_resource_id | UUID String |
| vector_store_type | VARCHAR(50) |
| vector_store_name | VARCHAR(100) |
| collection_name | VARCHAR(100) |
| index_name | VARCHAR(100) |
| embedding_model | VARCHAR(100) |
| is_primary | BOOLEAN |
| status | VARCHAR(15) |
| addl_data | JSON |
| created_dt | TIMESTAMP |
| updated_dt | TIMESTAMP |
| created_by | VARCHAR(50) |
| updated_by | VARCHAR(50) |

Supported Vector Stores:

- mongodb
- chromadb
- pgvector
- weaviate
- pinecone

---

## Company Resource Index Status

Tracks indexing progress.

| Field | Type |
|---------|---------|
| index_status_id | UUID String |
| company_id | UUID String |
| company_resource_id | UUID String |
| content_id | UUID String |
| vector_config_id | UUID String |
| vector_store_type | VARCHAR(50) |
| index_status | VARCHAR(30) |
| attempts | INTEGER |
| last_error | TEXT |
| indexed_dt | TIMESTAMP |
| created_dt | TIMESTAMP |
| updated_dt | TIMESTAMP |

Statuses:

```text
PENDING
IN_PROGRESS
COMPLETED
FAILED
SKIPPED
DEAD_LETTER
```

---

# Vector Store Strategy

A resource can be indexed into:

- One vector database
- Multiple vector databases

Examples:

```text
Resource A
   -> MongoDB Atlas Vector Search

Resource B
   -> MongoDB Atlas
   -> Pinecone

Resource C
   -> pgVector
   -> Weaviate
```

This is entirely configuration-driven.

No vector store selection is hardcoded.

---

# LangGraph Indexing Workflow

```text
Load Content
      |
      v
Load Vector Configuration
      |
      v
Chunk Content
      |
      v
Generate Embeddings
      |
      v
For Each Configured Vector Store
      |
      +--> Index Content
      +--> Update Status
      +--> Handle Errors
```

---

# MongoDB Collections

```text
companies
company_resources
company_resource_graph
company_resource_content
company_resource_vector_config
company_resource_index_status
workflow_runs
workflow_run_steps
customer_users
search_history
search_feedback
```

---

# Repository Structure

```text
vehicles-knowledge-platform/

├── admin-portal/
├── customer-portal/
├── airflow/
│   └── dags/
│
├── services/
│   ├── auth-service/
│   ├── company-service/
│   ├── discovery-service/
│   ├── crawler-service/
│   ├── extraction-service/
│   ├── embedding-service/
│   ├── search-service/
│   └── langgraph-agent-service/
│
├── mongodb/
├── infrastructure/
├── docs/
└── README.md
```

---

# Technology Stack

Frontend

- React
- Next.js

Backend

- Spring Boot
- Java 21

Workflow

- Apache Airflow
- LangGraph

AI

- OpenAI
- Azure OpenAI
- LangGraph

Vector Stores

- MongoDB Atlas Vector Search
- ChromaDB
- pgVector
- Weaviate
- Pinecone

Infrastructure

- Docker
- Kubernetes
- Terraform

Monitoring

- Prometheus
- Grafana
- OpenTelemetry

---

# Future Enhancements

- Knowledge Graph Generation
- Neo4j Integration
- Image Embeddings
- Video Embeddings
- Multi-modal Search
- Personalized Search
- Recommendation Engines
- Search Analytics Dashboard
- Human-in-the-loop Validation
- Agentic Research Assistants
- Vehicle Ontology Management

# Future Enhancements - Detailed

## Future Enhancements Roadmap

These enhancements evolve VKP from a search platform into a comprehensive Vehicle Intelligence Platform.

| Enhancement | What It Means | Example Use Case | Business Value |
|------------|---------------|------------------|----------------|
| Knowledge Graph Generation | Automatically create relationships between vehicles, manufacturers, technologies, features, documents, images, and people. | Vehicle A uses Battery Technology B supplied by Company C. | Enables relationship discovery, recommendations, and explainable AI. |
| Neo4j Integration | Store and query graph relationships using Neo4j in addition to MongoDB. | Find all vehicles using a specific ADAS technology. | High-performance graph traversal and relationship analytics. |
| Image Embeddings | Convert images into vectors for semantic image search. | User uploads a dashboard photo and searches for similar vehicle interiors. | Visual search capabilities beyond text. |
| Video Embeddings | Convert video frames and transcripts into searchable embeddings. | Search videos mentioning autonomous driving features. | Search across video content, demonstrations, and reviews. |
| Multi-modal Search | Search across text, images, videos, PDFs, and metadata simultaneously. | Show vehicles with panoramic sunroofs using images and descriptions. | Richer search experiences and better recall. |
| Personalized Search | Search results adapt to user behavior and preferences. | User prefers SUVs and hybrid vehicles. | Improved relevance and customer engagement. |
| Recommendation Engines | AI recommends related content, vehicles, documents, or resources. | User views an electric SUV and receives related comparisons. | Increased user retention and discovery. |
| Search Analytics Dashboard | Track search behavior, popular topics, failed searches, and content gaps. | Identify the most searched vehicle technologies this month. | Product insights and content strategy. |
| Human-in-the-loop Validation | Humans review AI-generated extractions, classifications, and indexing decisions. | Reviewer corrects an incorrectly classified vehicle feature. | Improves data quality and governance. |
| Agentic Research Assistants | AI agents perform multi-step research tasks autonomously. | Research all vehicles with Level 2 autonomous driving and summarize findings. | Moves beyond search into automated research. |
| Vehicle Ontology Management | Define a formal vocabulary and hierarchy for vehicle concepts. | SUV → Compact SUV → Electric Compact SUV. | Standardized data model and better search/filtering. |

---

# Recommended Implementation Order

| Phase | Enhancement | Priority |
|---------|---------|---------|
| Phase 1 | Search Analytics Dashboard | High |
| Phase 1 | Human-in-the-loop Validation | High |
| Phase 2 | Recommendation Engines | Medium |
| Phase 2 | Personalized Search | Medium |
| Phase 3 | Image Embeddings | High |
| Phase 3 | Multi-modal Search | High |
| Phase 4 | Video Embeddings | Medium |
| Phase 4 | Agentic Research Assistants | High |
| Phase 5 | Vehicle Ontology Management | High |
| Phase 5 | Knowledge Graph Generation | High |
| Phase 5 | Neo4j Integration | Optional |

---

# Suggested Strategic Roadmap

## Phase 1 - Platform Foundation

- Admin Portal
- Customer Portal
- Airflow
- LangGraph
- MongoDB
- Vector Search

## Phase 2 - Operational Intelligence

- Search Analytics Dashboard
- Feedback Loop
- Human Validation

## Phase 3 - Multi-modal Intelligence

- Image Embeddings
- Multi-modal Search

## Phase 4 - Agentic Intelligence

- Agentic Research Assistants

## Phase 5 - Knowledge Intelligence

- Vehicle Ontology Management
- Knowledge Graph Generation
- Neo4j Integration

---

# Long-Term Vision

The most strategically valuable future capabilities are:

1. Agentic Research Assistants
2. Multi-modal Search
3. Knowledge Graph Generation
4. Vehicle Ontology Management

Together these transform VKP from a search engine into a Vehicle Intelligence Platform where users can ask complex questions, navigate relationships, discover insights, and receive synthesized knowledge rather than simple search results.

# Application Architecture

## Vehicle Knowledge Platform (VKP)

This document defines the proposed application architecture and codebase structure for the Vehicle Knowledge Platform (VKP).

The architecture separates the platform into two major areas:

1. **Portals** - User-facing web applications.
2. **Middleware** - Backend services, orchestration APIs, crawling services, ingestion services, search services, and integration adapters.

---

# High-Level Repository Structure

```text
vehicles-knowledge-platform/

├── README.md
├── Application Architecture.md
├── Future_Enhancements.md
│
├── portals/
│   ├── admin-portal/
│   └── vehicle-search-portal/
│
├── middleware/
│   ├── admin-service/
│   ├── customer-management-service/
│   ├── user-management-service/
│   ├── data-collection-service/
│   ├── ingestion-service/
│   ├── airflow-adapter-service/
│   ├── vehicle-explore-service/
│   ├── vector-config-service/
│   └── common/
│
├── airflow/
│   └── dags/
│       ├── vkp_discover_resources.py
│       ├── vkp_process_resources.py
│       ├── vkp_extract_content.py
│       ├── vkp_langgraph_index_content.py
│       └── vkp_refresh_content.py
│
├── ai-frameworks/
│   ├── langgraph/
│   ├── crewai/
│   └── shared/
│
├── mongodb/
│   ├── collections/
│   ├── indexes/
│   └── vector-search/
│
├── infrastructure/
│   ├── docker/
│   ├── kubernetes/
│   └── terraform/
│
├── docs/
└── tests/
```

---

# Architecture Overview

```text
+-------------------------+        +------------------------------+
|      Admin Portal       |        |   Vehicle Search Portal      |
+------------+------------+        +---------------+--------------+
             |                                     |
             v                                     v
+-------------------------+        +------------------------------+
| Admin / Customer APIs   |        | User / Search APIs           |
+------------+------------+        +---------------+--------------+
             |                                     |
             v                                     v
+---------------------------------------------------------------+
|                         Middleware                            |
|---------------------------------------------------------------|
| Admin Service                                                |
| Customer Management Service                                  |
| User Management Service                                      |
| Data Collection Service                                      |
| Ingestion Service                                            |
| Airflow Adapter Service                                      |
| Vehicle Explore Service                                      |
| Vector Config Service                                        |
+----------------------------+----------------------------------+
                             |
                             v
+---------------------------------------------------------------+
|                       Apache Airflow                         |
|---------------------------------------------------------------|
| Resource Discovery DAGs                                      |
| Resource Processing DAGs                                     |
| Content Extraction DAGs                                      |
| LangGraph Indexing DAGs                                      |
| Refresh DAGs                                                 |
+----------------------------+----------------------------------+
                             |
                             v
+---------------------------------------------------------------+
|                         MongoDB                              |
|---------------------------------------------------------------|
| Company                                                       |
| Company Resource                                              |
| Company Resource Graph                                        |
| Company Resource Content                                      |
| Vector Configuration                                          |
| Index Status                                                  |
| Customers / Users                                             |
| Search History                                                |
+----------------------------+----------------------------------+
                             |
                             v
+---------------------------------------------------------------+
|                 Vector Databases / AI Search                  |
|---------------------------------------------------------------|
| MongoDB Atlas Vector Search                                   |
| ChromaDB                                                      |
| pgVector                                                      |
| Weaviate                                                      |
| Pinecone                                                      |
| LangGraph / CrewAI / Other AI Frameworks                      |
+---------------------------------------------------------------+
```

---

# Portals

## 1. Admin Portal

The Admin Portal is used by internal administrators and operators.

### Responsibilities

- Company management
- Customer management
- Company resource management
- Resource discovery trigger
- Ingestion trigger
- Crawl monitoring
- Workflow monitoring
- Failed resource review
- Retry and reprocessing
- Vector database configuration
- Audit and status review

### Talks To

```text
Admin Portal
   -> Admin Service
   -> Customer Management Service
   -> Data Collection Service
   -> Ingestion Service
   -> Airflow Adapter Service
   -> Vector Config Service
```

---

## 2. Vehicle Search Portal

The Vehicle Search Portal is used by end users/customers.

### Responsibilities

- Signup
- Signin
- User profile
- Password reset
- Search vehicle knowledge
- View AI-generated search results
- View result images
- View suitable source links
- Save searches
- View search history
- Provide feedback

### Talks To

```text
Vehicle Search Portal
   -> User Management Service
   -> Vehicle Explore Service
```

---

# Middleware Services

## 1. Admin Service

Recommended technology:

```text
Spring Boot
Java 21
MongoDB
```

### Responsibilities

- Admin authentication integration
- Admin dashboard APIs
- Company CRUD
- High-level platform configuration
- Admin audit APIs
- Workflow status APIs

### Example APIs

```http
GET    /api/admin/dashboard
POST   /api/admin/companies
GET    /api/admin/companies/{companyId}
PUT    /api/admin/companies/{companyId}
DELETE /api/admin/companies/{companyId}
```

---

## 2. Customer Management Service

Recommended technology:

```text
Spring Boot
Java 21
MongoDB
```

### Purpose

This service is used mainly by the Admin Portal to manage customers and their associated resources.

### Responsibilities

- Customer CRUD
- Customer company mapping
- Customer resource mapping
- Customer status management
- Customer audit tracking
- Customer-level resource configuration

### Example APIs

```http
POST   /api/admin/customers
GET    /api/admin/customers
GET    /api/admin/customers/{customerId}
PUT    /api/admin/customers/{customerId}
DELETE /api/admin/customers/{customerId}

POST   /api/admin/customers/{customerId}/resources
GET    /api/admin/customers/{customerId}/resources
PUT    /api/admin/customers/{customerId}/resources/{resourceId}
DELETE /api/admin/customers/{customerId}/resources/{resourceId}
```

---

## 3. User Management Service

Recommended technology:

```text
Spring Boot
Java 21
MongoDB
JWT / OAuth2
```

### Purpose

This service supports the Vehicle Search Portal.

### Responsibilities

- Signup
- Signin
- Password reset
- Email verification
- JWT token generation
- User profile management
- Role management
- Search portal access control

### Example APIs

```http
POST /api/users/signup
POST /api/users/signin
POST /api/users/forgot-password
POST /api/users/reset-password
GET  /api/users/profile
PUT  /api/users/profile
```

---

## 4. Data Collection Service

Recommended technology:

```text
Spring Boot
Java 21
MongoDB
Apache Airflow Integration
```

### Purpose

The Data Collection Service is responsible for discovering links only.

It does not crawl each page for full content extraction. Instead, it identifies links, images, documents, and resource graph nodes, and stores them in the data model.

### Responsibilities

- Read company resources
- Trigger link discovery workflows
- Invoke Apache Airflow through Airflow Adapter Service
- Discover website links
- Discover sitemap URLs
- Discover images and document URLs
- Store discovered resources in Company Resource Graph
- Update discovery statuses

### Example APIs

```http
POST /api/data-collection/companies/{companyId}/resources/{resourceId}/discover
GET  /api/data-collection/companies/{companyId}/resources/{resourceId}/status
GET  /api/data-collection/companies/{companyId}/resource-graph
```

### Airflow DAG Invoked

```text
vkp_discover_resources
```

---

## 5. Ingestion Service

Recommended technology:

```text
Spring Boot
Java 21
MongoDB
Apache Airflow Integration
```

### Purpose

The Ingestion Service is responsible for crawling actual discovered links and updating their processing status.

It handles the operational control for full page crawling, content extraction, status tracking, and downstream indexing.

### Responsibilities

- Read discovered links from Company Resource Graph
- Trigger crawl workflows
- Invoke Apache Airflow through Airflow Adapter Service
- Track page crawl status
- Update Company Resource Graph status
- Store extracted content in Company Resource Content
- Trigger LangGraph indexing workflow through Airflow
- Track indexing progress

### Example APIs

```http
POST /api/ingestion/companies/{companyId}/resources/{resourceId}/crawl
POST /api/ingestion/companies/{companyId}/resources/{resourceId}/index
GET  /api/ingestion/companies/{companyId}/resources/{resourceId}/status
GET  /api/ingestion/content/{contentId}
```

### Airflow DAGs Invoked

```text
vkp_process_resources
vkp_extract_content
vkp_langgraph_index_content
vkp_refresh_content
```

---

## 6. Airflow Adapter Service

Recommended technology:

```text
Spring Boot
Java 21
Apache Airflow REST API
```

### Purpose

The Airflow Adapter Service centralizes all communication with Apache Airflow.

No portal or business service should directly call Airflow. All Airflow interaction goes through this adapter.

### Responsibilities

- Trigger Airflow DAGs
- Pass DAG runtime parameters
- Query DAG run status
- Query task status
- Retry failed DAG runs
- Cancel DAG runs
- Normalize Airflow responses
- Hide Airflow implementation details from other services

### Example APIs

```http
POST /api/airflow/dags/{dagId}/trigger
GET  /api/airflow/dags/{dagId}/runs/{runId}
GET  /api/airflow/dags/{dagId}/runs/{runId}/tasks
POST /api/airflow/dags/{dagId}/runs/{runId}/retry
POST /api/airflow/dags/{dagId}/runs/{runId}/cancel
```

### Example Trigger Payload

```json
{
  "company_id": "uuid",
  "company_resource_id": "uuid",
  "triggered_by": "admin-user",
  "run_type": "ON_DEMAND",
  "options": {
    "force_refresh": false,
    "max_pages": 1000
  }
}
```

---

## 7. Vector Config Service

Recommended technology:

```text
Spring Boot
Java 21
MongoDB
```

### Purpose

This service manages vector database configuration for each company resource.

A single company resource can be indexed into one or more vector databases.

### Responsibilities

- Create vector store configuration
- Update vector store configuration
- Enable or disable vector targets
- Configure embedding model
- Configure collection name
- Configure index name
- Configure primary vector store
- Provide configuration to LangGraph ingestion workflow

### Example APIs

```http
POST /api/vector-config/company-resources/{companyResourceId}
GET  /api/vector-config/company-resources/{companyResourceId}
PUT  /api/vector-config/{vectorConfigId}
DELETE /api/vector-config/{vectorConfigId}
```

### Supported Vector Stores

```text
mongodb
chromadb
pgvector
weaviate
pinecone
```

---

## 8. Vehicle Explore Service

Recommended technology:

```text
Python
Flask or FastAPI
LangGraph
CrewAI
LLM Integrations
Vector Database Integrations
```

### Purpose

The Vehicle Explore Service powers the AI search experience for the Vehicle Search Portal.

This service is intentionally designed in Python because Python integrates easily with:

- LangGraph
- CrewAI
- LlamaIndex
- Haystack
- OpenAI SDKs
- Vector database SDKs

### Responsibilities

- Accept customer search queries
- Route query to selected AI framework
- Support LangGraph search workflow
- Support CrewAI or other frameworks in the future
- Perform vector search
- Perform hybrid search if needed
- Retrieve image metadata
- Retrieve suitable source links
- Generate LLM response
- Return structured result cards

---

# AI Framework Routing

To support multiple AI orchestration frameworks, the framework name should be part of the URL.

This allows the platform to route requests dynamically to different implementations.

## Example URL Pattern

```http
POST /api/vehicle-explore/{frameworkName}/search
```

Examples:

```http
POST /api/vehicle-explore/langgraph/search
POST /api/vehicle-explore/crewai/search
POST /api/vehicle-explore/llamaindex/search
POST /api/vehicle-explore/haystack/search
```

## Example Search Request

```json
{
  "customer_id": "uuid",
  "query": "Show vehicles with advanced safety features and interior images",
  "filters": {
    "resource_type": ["website", "pdf"],
    "include_images": true,
    "include_links": true
  }
}
```

## Example Search Response

```json
{
  "framework": "langgraph",
  "query": "Show vehicles with advanced safety features and interior images",
  "rewritten_query": "advanced vehicle safety features interior images",
  "answer": "Here are the most relevant results related to advanced safety features.",
  "results": [
    {
      "title": "Vehicle Safety Features",
      "summary": "This page describes advanced driver assistance, collision warnings, and safety technologies.",
      "source_url": "https://example.com/vehicle/safety",
      "score": 0.91,
      "images": [
        {
          "image_url": "https://example.com/images/safety.jpg",
          "alt_text": "Vehicle safety feature image",
          "caption": "Safety technology overview"
        }
      ],
      "links": [
        {
          "label": "View Source",
          "url": "https://example.com/vehicle/safety"
        }
      ]
    }
  ]
}
```

---

# Service Interaction Flow

## Admin Resource Discovery Flow

```text
Admin Portal
   |
   v
Data Collection Service
   |
   v
Airflow Adapter Service
   |
   v
Apache Airflow
   |
   v
vkp_discover_resources DAG
   |
   v
Company Resource Graph updated
```

---

## Admin Resource Ingestion Flow

```text
Admin Portal
   |
   v
Ingestion Service
   |
   v
Airflow Adapter Service
   |
   v
Apache Airflow
   |
   v
vkp_process_resources DAG
   |
   v
Discovered link crawled
   |
   v
Company Resource Content updated
   |
   v
vkp_langgraph_index_content DAG
   |
   v
LangGraph ingestion workflow
   |
   v
Configured vector databases updated
```

---

## Customer Search Flow

```text
Vehicle Search Portal
   |
   v
User Management Service
   |
   v
Vehicle Explore Service
   |
   v
Framework Router
   |
   +--> LangGraph Search Workflow
   +--> CrewAI Search Workflow
   +--> Other Framework Workflow
   |
   v
Vector Store Search
   |
   v
LLM Response Generation
   |
   v
Search results with images and links
```

---

# Data Model Alignment

The middleware services are built around the VKP data model.

## Core Collections

```text
companies
company_resources
company_resource_graph
company_resource_content
company_resource_vector_config
company_resource_index_status
workflow_runs
workflow_run_steps
customer_users
search_history
search_feedback
```

## Data Ownership

| Collection | Owning Service |
|---|---|
| companies | Admin Service |
| company_resources | Admin Service / Customer Management Service |
| company_resource_graph | Data Collection Service |
| company_resource_content | Ingestion Service |
| company_resource_vector_config | Vector Config Service |
| company_resource_index_status | Ingestion Service / LangGraph Indexing |
| workflow_runs | Airflow Adapter Service |
| workflow_run_steps | Airflow Adapter Service |
| customer_users | User Management Service |
| search_history | Vehicle Explore Service |
| search_feedback | Vehicle Explore Service |

---

# Technology Recommendations

## Spring Boot Services

Use Spring Boot for:

- Admin Service
- Customer Management Service
- User Management Service
- Data Collection Service
- Ingestion Service
- Airflow Adapter Service
- Vector Config Service

Why:

- Strong REST API support
- Enterprise security
- MongoDB integration
- Validation support
- Observability support
- Consistent service patterns

---

## Python AI Service

Use Python with Flask or FastAPI for:

- Vehicle Explore Service
- LangGraph workflow execution
- CrewAI workflow execution
- LLM search
- Vector database integrations

Recommendation:

```text
FastAPI is preferred for production APIs.
Flask is acceptable for simpler prototypes.
```

Why FastAPI:

- Async support
- OpenAPI documentation
- Strong typing with Pydantic
- Better fit for AI microservices
- Easy integration with LangGraph and vector database SDKs

---

# Deployment View

```text
Kubernetes Cluster

Namespace: vkp

Pods:
- admin-portal
- vehicle-search-portal
- admin-service
- customer-management-service
- user-management-service
- data-collection-service
- ingestion-service
- airflow-adapter-service
- vector-config-service
- vehicle-explore-service
- airflow-webserver
- airflow-scheduler
- airflow-workers

External Services:
- MongoDB Atlas
- MongoDB Atlas Vector Search
- Pinecone
- Weaviate
- ChromaDB
- PostgreSQL with pgVector
- LLM Provider
```

---

# Summary

The VKP application architecture uses:

- **Portals** for user-facing experiences
- **Middleware** for backend microservices
- **Spring Boot** for enterprise APIs and data model services
- **Apache Airflow** for workflow orchestration
- **Airflow Adapter Service** to centralize DAG execution
- **Data Collection Service** for link discovery only
- **Ingestion Service** for actual page crawling and status updates
- **LangGraph ingestion workflows** for chunking, embedding, and vector indexing
- **Vehicle Explore Service** for LLM-powered search
- **Framework-based routing** to support LangGraph, CrewAI, and other agent frameworks
- **Config-driven vector database indexing** across MongoDB, ChromaDB, pgVector, Weaviate, and Pinecone


