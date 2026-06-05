"""Prometheus metrics for the search pipeline (scraped at GET /metrics).

The latency Histogram lets Prometheus/Grafana compute P50/P95/P99 via histogram_quantile().
"""
from prometheus_client import Counter, Histogram

SEARCH_LATENCY = Histogram(
    "vkp_search_latency_seconds", "End-to-end search latency",
    ["framework", "store"],
    buckets=(0.1, 0.25, 0.5, 1, 2, 3, 5, 8, 13, 21))

SEARCHES = Counter(
    "vkp_searches_total", "Searches by outcome", ["framework", "store", "outcome"])  # ok|blocked|error

GUARDRAIL_BLOCKS = Counter(
    "vkp_guardrail_blocks_total", "Guardrail blocks", ["phase"])  # input|output

PROVIDER_ANSWERS = Counter(
    "vkp_provider_answers_total", "Per-provider answer outcomes", ["provider", "ok"])  # ok=true|false
