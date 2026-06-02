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
