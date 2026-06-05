"""OpenTelemetry distributed tracing setup for the guardrails service.

Auto-instruments FastAPI so incoming requests CONTINUE the trace started by the explore service
(the W3C traceparent header propagates over the explore->guardrails call), and urllib for any
outbound hop. Spans export via OTLP/HTTP to VKP_OTEL_ENDPOINT (default the Jaeger all-in-one).

Toggles: VKP_OTEL_ENABLED=false (off), VKP_OTEL_ENDPOINT=..., VKP_OTEL_CONSOLE=true (also print).
Best-effort: no-ops with a warning if the OTel libs aren't installed.
"""
import logging
import os

log = logging.getLogger("guardrails")


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
    URLLibInstrumentor().instrument()
    log.info("OpenTelemetry tracing -> %s (service=%s)", endpoint, service_name)
