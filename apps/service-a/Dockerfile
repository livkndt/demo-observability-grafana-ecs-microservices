FROM python:3.11-slim

WORKDIR /app

COPY libs/otel_sdk/dist/otel_sdk-0.1.0-py3-none-any.whl /wheels/
COPY apps/service-a/dist/service_a-0.1.0-py3-none-any.whl /wheels/

RUN pip install --no-cache-dir /wheels/*.whl

EXPOSE 8000

CMD ["uvicorn", "service_a.main:app", "--host", "0.0.0.0", "--port", "8000"]