import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

def _normalize_endpoint(raw_endpoint: str) -> str:
    # grpc exporter expects host:port; strip scheme if present
    if raw_endpoint.startswith("http://"):
        return raw_endpoint[len("http://"):]
    if raw_endpoint.startswith("https://"):
        return raw_endpoint[len("https://"):]
    return raw_endpoint


def configure_otel(service_name: str, endpoint: Optional[str] = None) -> None:
    resource = Resource(
        attributes={
            SERVICE_NAME: service_name,
            "environment": os.getenv("ENVIRONMENT", "dev"),
        }
    )
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    raw_endpoint = endpoint or os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "localhost:4317")
    otlp_exporter = OTLPSpanExporter(endpoint=_normalize_endpoint(raw_endpoint), insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)


def instrument_fastapi(app) -> None:
    FastAPIInstrumentor.instrument_app(app)


def instrument_requests() -> None:
    RequestsInstrumentor().instrument()


def get_current_trace_id() -> str:
    current_span = trace.get_current_span()
    span_context = current_span.get_span_context()
    trace_id = getattr(span_context, "trace_id", 0)
    return format(trace_id, "032x")
