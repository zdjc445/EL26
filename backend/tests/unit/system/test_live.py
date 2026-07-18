from fastapi.testclient import TestClient
from time_agent.bootstrap.app import create_app
from time_agent.config import Settings


def test_live_returns_versioned_service_identity() -> None:
    app = create_app(Settings(environment="test", build_sha="test-sha"))

    response = TestClient(app).get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "time-api",
        "version": "0.1.0",
        "build_sha": "test-sha",
    }


def test_openapi_uses_the_product_name_and_versioned_path() -> None:
    app = create_app(Settings(environment="test", build_sha="test-sha"))

    schema = app.openapi()

    assert schema["info"]["title"] == "Time API"
    assert schema["info"]["version"] == "0.1.0"
    assert "/api/v1/health/live" in schema["paths"]
