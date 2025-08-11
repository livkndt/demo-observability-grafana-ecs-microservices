from fastapi import FastAPI
from otel_sdk import configure_otel, instrument_fastapi, get_current_trace_id
from opentelemetry import trace

app = FastAPI()
configure_otel("service-b")
instrument_fastapi(app)

tracer = trace.get_tracer(__name__)

@app.get("/world")
def read_world():
    with tracer.start_as_current_span("service-b-span"):
        return {"message": "Hello from service B", "trace_id": get_current_trace_id()}
