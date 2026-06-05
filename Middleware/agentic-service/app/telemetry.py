"""OpenTelemetry distributed tracing setup.

Auto-instruments FastAPI (incoming requests) + urllib (the outbound call to guardrails, so the
W3C traceparent propagates and the explore->guardrails hop joins one trace). Spans are exported
via OTLP/HTTP to VKP_OTEL_ENDPOINT (default the Jaeger all-in-one at http://localhost:4318).

Toggles (env):
  VKP_OTEL_ENABLED=false   -> disable entirely (default on)
  VKP_OTEL_ENDPOINT=...     -> OTLP/HTTP base (default http://localhost:4318)
  VKP_OTEL_CONSOLE=true     -> also print spans to stdout (verify without a backend)

Best-effort: if the OTel libs aren't installed, logs a warning and no-ops (never breaks the app).
"""
import logging
import os

log = logging.getLogger("agentic")


def setup_tracing(app, service_name: str) -> None:
    if os.getenv("VKP_OTEL_ENABLED", "true").lower() not in ("1", "true", "yes"):
        return
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.urllib import URLLibInstrumentor
    except ImportError as e:  # noqa: BLE001
        log.warning("OpenTelemetry libs missing (%s); tracing disabled", e)
        return

    endpoint = os.getenv("VKP_OTEL_ENDPOINT", "http://localhost:4318").rstrip("/")
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")))
    if os.getenv("VKP_OTEL_CONSOLE", "").lower() in ("1", "true", "yes"):
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
    URLLibInstrumentor().instrument()   # propagate traceparent on the outbound guardrails call
    log.info("OpenTelemetry tracing -> %s (service=%s)", endpoint, service_name)
