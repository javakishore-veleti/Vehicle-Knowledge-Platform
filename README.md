# Vehicle Knowledge Platform (VKP)

## Overview

Vehicle Knowledge Platform (VKP) is an enterprise-grade platform for discovering, crawling, processing, embedding, and semantically searching vehicle-related digital content across multiple online resources.

The platform supports intelligent ingestion of publicly available automotive information including:

* Manufacturer websites
* Product and vehicle pages
* Blogs and articles
* Documentation
* Brochures
* Images
* PDFs
* Videos
* Social media resources

The platform is designed to provide a centralized vehicle knowledge repository that supports semantic search, Retrieval Augmented Generation (RAG), AI assistants, analytics, and future knowledge graph capabilities.

---

## Business Objectives

The platform enables organizations to:

* Discover vehicle-related digital resources
* Crawl and process automotive content
* Extract structured and unstructured vehicle information
* Generate vector embeddings
* Create a searchable vehicle knowledge repository
* Support semantic search experiences
* Enable AI-powered question answering
* Maintain complete auditability and workflow traceability

---

## Supported Resource Types

### Seed Resources

Examples include:

* Official vehicle websites
* Product catalogs
* Vehicle specification pages
* Vehicle brochures
* Automotive blogs
* Press releases
* Documentation portals
* Social media pages
* Video channels

### Discovered Resources

Examples include:

* Vehicle detail pages
* Model overview pages
* Vehicle comparison pages
* Feature descriptions
* Technology pages
* Image assets
* PDF brochures
* Videos
* Downloadable documentation

---

## Platform Architecture

```text
Admin Portal
    |
    v
Apache Airflow
    |
    +---------------------+
    |                     |
    v                     v

Resource Discovery   Resource Processing

    |                     |
    v                     v

MongoDB Atlas

Collections:
- Company
- Company Resource
- Resource Graph
- Resource Content
- Workflow Runs

    |
    v

Embedding Generation

    |
    v

MongoDB Atlas Vector Search

    |
    v

LangGraph Search Application

    |
    v

Vehicle Knowledge Retrieval
```

---

## Core Capabilities

### Resource Discovery

Identify and catalog vehicle-related resources from configured seed locations.

### Content Extraction

Extract:

* Vehicle descriptions
* Vehicle features
* Technical specifications
* Safety information
* Technology information
* Marketing content
* Media assets

### Embedding Generation

Generate vector embeddings from extracted content to enable semantic retrieval.

### Semantic Search

Support natural language questions such as:

* Find vehicles with advanced safety features
* Search vehicles by technology offerings
* Compare vehicle descriptions
* Find content related to specific capabilities
* Retrieve vehicle knowledge using conversational queries

### AI-Powered Knowledge Retrieval

Leverage LangGraph orchestration and vector search to provide intelligent answers from the platform's knowledge base.

---

## Repository Name

```text
vehicles-knowledge-platform
```

Abbreviation:

```text
VKP
```

Example Services:

```text
vkp-admin-service
vkp-discovery-service
vkp-crawler-service
vkp-extraction-service
vkp-embedding-service
vkp-search-service
vkp-langgraph-service
```

Example Airflow DAGs:

```text
vkp_discover_resources
vkp_process_resources
vkp_generate_embeddings
vkp_refresh_content
```

---

## Future Enhancements

* Vehicle taxonomy management
* Vehicle ontology support
* Knowledge graph generation
* Multi-modal search
* Image embeddings
* Video embeddings
* Vehicle comparison intelligence
* Change detection and monitoring
* Agentic research assistants
* Recommendation engines
* Neo4j integration
* Human-in-the-loop validation workflows
