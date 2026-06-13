"""Catalog of the 5 VKP use cases per pattern (from the Agentic Patterns page).
IMPLEMENTED = the (pattern, framework, useCase) cells that run a use-case-specific flow (vs the generic)."""
CATALOG = {
    "reflection": [("answer-quality-gate", "Answer quality gate"), ("chunk-quality-review", "Chunk quality review"),
                   ("citation-verification", "Citation verification"), ("crawl-coverage-self-check", "Crawl coverage self-check"),
                   ("spec-extraction-accuracy", "Spec-extraction accuracy")],
    "react": [("smart-link-discovery", "Smart link discovery"), ("single-model-deep-dive", "Single-model deep-dive"),
              ("recall-safety-lookup", "Recall / safety lookup"), ("dealer-inventory-locator", "Dealer / inventory locator"),
              ("broken-link-repair", "Broken-link repair")],
    "plan-execute": [("multi-brand-comparison", "Multi-brand comparison search"), ("buyers-guide-builder", "Buyer's-guide builder"),
                     ("adaptive-onboarding", "Adaptive company onboarding"), ("spec-sheet-assembly", "Spec-sheet assembly"),
                     ("tco-report", "Total-cost-of-ownership report")],
    "rewoo": [("batch-spec-enrichment", "Batch spec enrichment"), ("parallel-multi-brand-facts", "Parallel multi-brand facts"),
              ("nightly-price-refresh", "Nightly price refresh"), ("bulk-image-alt-text", "Bulk image alt-text"),
              ("fixed-dimension-comparison", "Fixed-dimension comparison")],
    "tot": [("best-car-for-me", "\"Best car for me\""), ("ambiguous-query", "Ambiguous-query disambiguation"),
            ("trim-optimizer", "Trim / option optimizer"), ("multi-constraint-filter", "Multi-constraint filter"),
            ("spec-conflict-resolver", "Spec-conflict resolver")],
    "router": [("compound-vs-simple", "Compound-vs-simple routing"), ("framework-router", "Framework router"),
               ("query-type-router", "Query-type router"), ("store-router", "Store router"),
               ("topic-guardrail-router", "Topic / guardrail router")],
    "rag": [("single-fact-qa", "Single-fact vehicle Q&A"), ("company-scoped-faq", "Company-scoped FAQ"),
            ("brochure-pdf-lookup", "Brochure / PDF lookup"), ("explain-feature", "\"Explain this feature\""),
            ("snapshot-grounded", "Snapshot-grounded answer")],
    "multi-agent": [("researcher-advisor", "Researcher + advisor crew"), ("per-brand-workers", "Per-brand workers"),
                    ("onboarding-crew", "Onboarding crew"), ("review-aggregator", "Review aggregator"),
                    ("spec-price-safety", "Spec / price / safety specialists")],
    "evaluator-optimizer": [("answer-refiner", "Answer refiner"), ("chunking-optimizer", "Chunking optimizer"),
                            ("query-rewriter", "Query rewriter"), ("summary-tightener", "Summary tightener"),
                            ("embedding-model-selector", "Embedding-model selector")],
    "chaining": [("multi-provider-fanout", "Multi-provider answer fan-out"), ("ingestion-chain", "Ingestion chain"),
                 ("sectioning", "Sectioning"), ("voting", "Voting"), ("translate-then-index", "Translate-then-index")],
}

# (pattern, framework, useCase) cells with a real use-case-specific implementation.
IMPLEMENTED = ({("reflection", "langgraph", uc) for uc, _ in CATALOG["reflection"]}
               | {("rag", "langgraph", uc) for uc, _ in CATALOG["rag"]}
               | {("evaluator-optimizer", "langgraph", uc) for uc, _ in CATALOG["evaluator-optimizer"]}
               | {("router", "langgraph", uc) for uc, _ in CATALOG["router"]}
               | {("plan-execute", "langgraph", uc) for uc, _ in CATALOG["plan-execute"]}
               | {("multi-agent", "langgraph", uc) for uc, _ in CATALOG["multi-agent"]}
               | {("rewoo", "langgraph", uc) for uc, _ in CATALOG["rewoo"]}
               | {("tot", "langgraph", uc) for uc, _ in CATALOG["tot"]})


def for_pattern(pattern: str) -> list:
    out = []
    for uc, name in CATALOG.get(pattern, []):
        fws = sorted({fw for (p, fw, u) in IMPLEMENTED if p == pattern and u == uc})
        out.append({"id": uc, "name": name, "implementedIn": fws})
    return out
