from fastapi import FastAPI
from otel_sdk import (
    configure_otel,
    instrument_fastapi,
    instrument_requests,
    get_current_trace_id,
)
from opentelemetry import trace
import requests

app = FastAPI()
configure_otel("service-a")
instrument_fastapi(app)
instrument_requests()

tracer = trace.get_tracer(__name__)

@app.get("/hello")
def read_hello():
    with tracer.start_as_current_span("say_hello"):
        return {"message": "Hello from service A", "trace_id": get_current_trace_id()}

@app.get("/call-b")
def call_service_b():
    with tracer.start_as_current_span("call_service_b") as span:
        span.set_attribute("app.target_service", "service-b")
        span.set_attribute("app.action", "get_world")
        response = requests.get("http://127.0.0.1:8001/world", timeout=5)
        b_payload = response.json()
        return {"from_b": b_payload, "trace_id": get_current_trace_id()}
