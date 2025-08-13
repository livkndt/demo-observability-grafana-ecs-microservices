import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

import logging
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler, LogRecordProcessor
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter 

def configure_otel_tracing(resource: Resource) -> None:
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)

    otlp_exporter = OTLPSpanExporter(insecure=True)
    span_processor = BatchSpanProcessor(otlp_exporter)
    provider.add_span_processor(span_processor)

def configure_otel_logging(resource: Resource) -> None:
    logger_provider = LoggerProvider(resource=resource)
    set_logger_provider(logger_provider)

    otlp_exporter = OTLPLogExporter(insecure=True) # Send logs to Grafana Alloy (default OTLP 4317)

    logger_provider.add_log_record_processor(BatchLogRecordProcessor(otlp_exporter))

    # Attach the OpenTelemetry handler to std python logger
    handler = LoggingHandler(level=logging.INFO, logger_provider=logger_provider)
    logging.getLogger().addHandler(handler)
    logging.getLogger().setLevel(logging.INFO)

def instrument_fastapi(app, service_name: str) -> None:
    resource = Resource(
        attributes={
            SERVICE_NAME: service_name,
            "environment": os.getenv("ENVIRONMENT", "dev"),
        }
    )
    configure_otel_tracing(resource)
    configure_otel_logging(resource)

    FastAPIInstrumentor.instrument_app(app)
    RequestsInstrumentor().instrument()

def get_current_trace_id() -> str:
    current_span = trace.get_current_span()
    span_context = current_span.get_span_context()
    trace_id = getattr(span_context, "trace_id", 0)
    return format(trace_id, "032x")
