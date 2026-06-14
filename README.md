# Vehicle Knowledge Platform (VKP)

> An enterprise platform that turns the scattered, public, multi-format world of vehicle content
> into a single trustworthy, conversational knowledge experience — and, in doing so, serves as a
> production-grade reference implementation of the modern agentic-AI stack.

This README is the **business and architecture narrative**. It deliberately does not catalogue
folders, database tables, or code — those are self-evident from the repository and are documented for
builders in [`CLAUDE.md`](CLAUDE.md) and the per-service `Development_Tracker.md` files. What follows
is *why this exists, what it must solve, how it is shaped, who it is for, how it is governed, what it
runs on, and how we know it is working.*

---

## 1. Business Context

Vehicle information is everywhere and trustworthy nowhere in particular. A buyer, a fleet operator,
a dealer, or an internal analyst trying to answer a simple question — *"Does this truck tow more than
that one?"*, *"What is the real five-year cost of ownership?"*, *"Are there open recalls?"* — must
stitch the answer together from manufacturer sites, brochures, spec sheets, PDFs, blogs, images,
videos, and social posts. The content is **public but fragmented, current but unstructured, rich but
unverifiable**.

At the same time, every organization that touches vehicles — OEMs, marketplaces, dealer groups,
insurers, fleet managers — is under pressure to deliver **AI-native, conversational experiences** that
are accurate, source-cited, and safe. The capability to *discover, ingest, understand, and answer over*
a domain's public content has become a competitive necessity rather than an experiment.

VKP exists at this intersection: a platform for **discovering, crawling, extracting, embedding, and
semantically searching vehicle-related content**, paired with a deliberate mandate to **master and
demonstrate the full agentic-AI engineering stack** on a real, non-trivial domain.

---

## 2. Business Problem

The platform is accountable for closing four concrete gaps:

| Gap | The problem in business terms |
|---|---|
| **Discovery** | Relevant vehicle content is spread across thousands of pages and formats with no canonical index. Finding *what to know* is itself unsolved. |
| **Trust** | Generative answers are only valuable if they are **grounded and cited**. Hallucinated specs or prices are worse than no answer — they are a liability. |
| **Safety & cost** | Conversational systems must refuse unsafe or off-topic requests, control spend, and remain auditable — by design, not by luck. |
| **Velocity** | The agentic-AI landscape changes monthly. An organization needs a way to **evaluate frameworks, patterns, and models objectively** instead of betting on one vendor. |

The unifying problem statement: **deliver accurate, cited, safe, conversational answers over a domain's
public content — while remaining free to choose the best AI framework, pattern, model, and vector store
for each job, and to prove that choice with evidence.**

---

## 3. Architecture Vision

VKP is shaped by a small number of load-bearing convictions. Each is a deliberate response to the
problems above, and each is designed to outlast any single technology choice.

- **Discovery and ingestion are separate disciplines.** *Discovering* the graph of links is a
  different problem — with different cost, cadence, and failure modes — from *fetching and
  understanding* the content behind them. Treating them as one pipeline is the most common reason
  these systems become unmaintainable. VKP keeps them as distinct, independently scalable stages.

- **Orchestration is owned, never embedded.** All long-running, retryable, observable work runs under
  **Apache Airflow**, reached through a **single adapter boundary**. No business service talks to the
  orchestrator directly. This keeps workflow concerns out of product code and makes the pipeline
  auditable end to end.

- **The knowledge store is a configuration, not a commitment.** Any piece of content can be indexed
  into one or many vector stores, selected per resource. The platform is **never hardcoded to a single
  vector database**, so the storage decision can follow cost, latency, and compliance — not yesterday's
  default.

- **The AI framework is a routing decision, not an architecture.** Search and reasoning are routed to a
  named framework at the edge. This makes the most volatile part of the stack — the agent framework —
  **pluggable and comparable**, and turns "which framework?" from a one-way door into an experiment.

- **Grounded, cited, guarded by default.** Answers are assembled from retrieved, attributable sources;
  unsafe and off-topic requests are blocked at a dedicated guardrail boundary; every request is logged
  for audit. Trust and safety are platform properties, not features bolted onto a prompt.

- **The domain is also a teaching instrument.** VKP doubles as an **agentic-AI mastery lab**: the same
  ten canonical agent patterns are implemented across eight industry frameworks and exercised against
  the same five concrete vehicle use cases — a living, runnable matrix that lets the organization choose
  with evidence rather than hype.

---

## 4. Stakeholder Alignment

The platform is designed so that each audience gets a surface shaped to its job, drawing on a shared
spine of services and data.

| Stakeholder | What they need | How VKP serves it |
|---|---|---|
| **End users / buyers** | Fast, trustworthy, cited answers | A conversational **Vehicle Search** experience returning answers with snippets, images, source links, and citations |
| **Operators / admins** | Control of what is discovered, ingested, and indexed | An **Admin** control plane to manage companies, run discovery/ingestion/indexing, and inspect every workflow |
| **AI / platform engineers** | A safe place to compare frameworks, patterns, and models | An interactive **agent-patterns lab** — every pattern × framework × use-case runnable live, side by side |
| **Risk, security & compliance** | Assurance that answers are safe, sourced, and auditable | Guardrails, session security, and full request telemetry as first-class, always-on boundaries |
| **Leadership** | A defensible, vendor-neutral AI capability with measurable results | A configuration-driven architecture that avoids lock-in and reports its own outcomes |

Three purpose-built portals — **Admin**, **Vehicle Search**, and a **Context-Engineering** workbench —
keep these conversations distinct while sharing one governed backend.

---

## 5. Governance

Governance in VKP is expressed as **architectural rules that the system enforces**, not as documents it
hopes people read. The load-bearing constraints:

- **One door to orchestration.** Every interaction with Airflow flows through a single adapter service.
  No portal or business service may trigger, query, or cancel a workflow directly — so orchestration is
  observable, rate-limited, and replaceable from one place.
- **A clear line between discovery and ingestion.** Link discovery may never silently fetch and store
  content; content ingestion may never quietly re-crawl. The boundary is structural, which keeps cost
  and provenance honest.
- **Configuration-driven storage.** No service hardcodes a vector store. Index targets are declared per
  resource and resolved at run time.
- **Safety and audit as boundaries, not options.** Guardrails screen requests for safety and topic;
  session security protects identity; every query is recorded. These are always on.
- **Grounding and citation as acceptance criteria.** An answer that cannot point to its sources is
  treated as a defect, not a stylistic preference.
- **Reproducible operations.** The platform runs from a single operational entrypoint locally and a
  categorized, cherry-pickable path to the cloud — so "how it runs" is itself governed and repeatable.

These rules are intentionally few. Their job is to make the *expensive-to-reverse* decisions explicit
and to leave the *cheap-to-change* ones — frameworks, models, stores — genuinely changeable.

---

## 6. Technology

Technology choices are made to honour the vision above: **owned orchestration, pluggable intelligence,
configurable storage, and provable safety.** At a strategic level:

- **Orchestration** — Apache Airflow runs the discovery, ingestion, and indexing pipelines behind a
  single governed adapter.
- **Agentic intelligence** — the reasoning layer is framework-neutral. VKP implements the modern
  agent-pattern catalogue across **eight frameworks**: LangGraph, CrewAI, LlamaIndex, Haystack, the
  OpenAI Agents SDK, Google ADK, the Microsoft Agent Framework, and AWS Strands.
- **Knowledge stores** — embeddings are indexed into configurable vector databases (MongoDB Atlas
  Vector Search, pgVector, ChromaDB, Weaviate, Pinecone), chosen per resource.
- **Operational data** — MongoDB and Postgres hold the platform's operational, metadata, and graph
  records.
- **Experiences** — three Angular portals for administration, search, and context-engineering.
- **Services** — a fleet of microservices (Java / Spring Boot and Python / FastAPI) behind versioned,
  audience-scoped APIs, each with health, metrics, and tracing built in.
- **Safety & trust** — dedicated guardrails, session security, and request telemetry.
- **Delivery** — containerized locally and deployable to the cloud via a categorized, cost-optimized,
  cherry-pickable infrastructure path.

The throughline: **no single vendor or framework is structural.** Each can be swapped without
reshaping the platform — which is the entire point.

---

## 7. Measurable Outcome

VKP holds itself to outcomes a business can verify, not capabilities a demo can imply.

- **Answer quality** — every response is **grounded and source-cited**; ungrounded answers are treated
  as defects. Quality is gated by an explicit evaluate-and-refine loop rather than assumed.
- **Safety** — unsafe and off-topic requests are **blocked at the guardrail boundary**, demonstrably,
  before they reach a model.
- **Vendor neutrality, proven** — the agent-pattern matrix is **complete and runnable**: ten canonical
  patterns, eight frameworks, five concrete vehicle use cases — **every cell verified live**, with the
  *deterministic* parts of each pattern producing identical results across all eight frameworks. The
  organization can compare frameworks on real work, on demand, and choose with evidence.
- **Auditability** — every request is logged with its reasoning steps, so any answer can be traced to
  its sources and its path.
- **Operability** — the whole platform starts, stops, and reports status from one entrypoint locally,
  and follows a repeatable, cost-aware path to the cloud.

The measurable promise, stated plainly: **accurate, cited, safe answers over public vehicle content —
delivered on a vendor-neutral architecture whose every AI choice is backed by a live, comparable,
reproducible result.**

---

### For builders

This document is intentionally strategic. Engineers looking for the as-built layout, service
conventions, run commands, data model, and the full agentic-pattern matrix should start with
[`CLAUDE.md`](CLAUDE.md) and the `Development_Tracker.md` files under each service. Run everything
locally from the repository root with `npm run localhost:start-all`.
