from fastapi import FastAPI
from otel_sdk import (
    instrument_fastapi,
    get_current_trace_id,
)
from opentelemetry import trace
import logging

app = FastAPI()
instrument_fastapi(app, "service-b")

tracer = trace.get_tracer(__name__)
logger = logging.getLogger(__name__)

@app.get("/world")
def read_world():
    with tracer.start_as_current_span("say_world"):
        logger.info("Hello log from service B!")
        return {"message": "Hello from service B", "trace_id": get_current_trace_id()}
