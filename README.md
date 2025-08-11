## Demo Observability: Grafana Alloy + FastAPI microservices

Two FastAPI services with OpenTelemetry tracing, exporting to Grafana Alloy.

### Project layout
- `apps/service-a`: FastAPI service A (calls service B via `/call-b`)
- `apps/service-b`: FastAPI service B
- `libs/otel_sdk`: Shared OpenTelemetry helpers (`configure_otel`, instrumentation)
- `config.alloy`: Grafana Alloy pipeline (OTLP in → OTLP out)
- `docker-compose.yml`: Runs Grafana Alloy locally

### Prerequisites
- Python 3.11
- Hatch (`pipx install hatch` or `pip install hatch`)
- Docker (for Grafana Alloy)

### Configuration
Copy the example env file and adjust if needed:
```bash
cp .env.example .env
```
Defaults export OTLP to `localhost:4317` and expose service ports `8000`/`8001`.

### Run Grafana Alloy
```bash
docker compose up -d alloy
```
This exposes:
- OTLP gRPC: `4317`
- OTLP HTTP: `4318`
- Alloy UI: `12345` (http://localhost:12345)

### Run the services (local)
Service B (port 8001):
```bash
cd apps/service-b
hatch env create
hatch run start
```

Service A (port 8000):
```bash
cd apps/service-a
hatch env create
hatch run start
```

### Try it
- Service A hello:
```bash
curl http://127.0.0.1:8000/hello
```
- Service B world:
```bash
curl http://127.0.0.1:8001/world
```
- Cross-service call (A → B with trace propagation):
```bash
curl http://127.0.0.1:8000/call-b
```
Responses include a `trace_id` (32-hex). You should see the same trace across both services in your backend.

### Environment variables
Used by the app and Alloy (see `config.alloy` and `.env.example`):
- `OTEL_EXPORTER_OTLP_ENDPOINT` (e.g., `localhost:4317` or Grafana Cloud endpoint)
- `ENVIRONMENT` (default `dev`)
- `SERVICE_A_PORT`, `SERVICE_B_PORT` (documented defaults; scripts currently use 8000/8001)

### Tests
Service A tests:
```bash
cd apps/service-a
hatch run test
```

### Troubleshooting
- IDE import errors (e.g., "fastapi could not be resolved"): point your IDE interpreter to the Hatch env for that service.
- If instrumentation warns about `pkg_resources` deprecation, it’s harmless for local dev.

### License
MIT
