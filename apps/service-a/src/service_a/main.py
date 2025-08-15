from fastapi import FastAPI
from otel_sdk import (
    instrument_fastapi,
    get_current_trace_id,
)
from opentelemetry import trace
import requests
import logging
import os

app = FastAPI()
instrument_fastapi(app, "service-a")

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/hello")
def read_hello():
    with tracer.start_as_current_span("say_hello"): 
        logger.info("This is an OpenTelemetry-enabled log message!")
        logger.warning("This is an OpenTelemetry-enabled warning message!")
        logger.debug("This is an OpenTelemetry-enabled debug message!")
        logger.error("This is an OpenTelemetry-enabled error!", extra={"error_code": 500})
        return {"message": "Hello from service A", "trace_id": get_current_trace_id()}

@app.get("/call-b")
def call_service_b():
    with tracer.start_as_current_span("call_service_b") as span:
        span.set_attribute("app.target_service", "service-b")
        span.set_attribute("app.action", "get_world")
        # Use service name for container networking
        service_b_url = os.getenv("SERVICE_B_URL", "http://service-b:8001")
        response = requests.get(f"{service_b_url}/world", timeout=5)
        b_payload = response.json()
        return {"from_b": b_payload, "trace_id": get_current_trace_id()}
