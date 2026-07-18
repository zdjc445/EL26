import pytest
from fastapi.testclient import TestClient
from time_agent.bootstrap.app import create_app
from time_agent.config import Settings


@pytest.mark.integration
def test_live_operation_is_present_in_the_served_openapi_contract() -> None:
    app = create_app(Settings(environment="test", build_sha="contract-test"))

    response = TestClient(app).get("/openapi.json")

    assert response.status_code == 200
    operation = response.json()["paths"]["/api/v1/health/live"]["get"]
    assert operation["operationId"] == "getLiveStatus"
    assert operation["responses"]["200"]["content"]["application/json"]["schema"] == {
        "$ref": "#/components/schemas/LiveStatus"
    }
