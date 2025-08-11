from unittest.mock import patch
from fastapi.testclient import TestClient
from service_a.main import app

client = TestClient(app)

def test_hello_returns_trace_id():
    response = client.get("/hello")
    assert response.status_code == 200
    body = response.json()
    assert body["message"] == "Hello from service A"
    assert isinstance(body.get("trace_id"), str)
    assert len(body["trace_id"]) == 32

@patch("service_a.main.requests.get")
def test_call_b_propagates_and_returns_trace_id(mock_get):
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"message": "Hello from service B", "trace_id": "x" * 32}

    response = client.get("/call-b")

    assert response.status_code == 200
    body = response.json()
    assert body["from_b"]["message"] == "Hello from service B"
    assert isinstance(body.get("trace_id"), str)
    assert len(body["trace_id"]) == 32

    mock_get.assert_called_once()
