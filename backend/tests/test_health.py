from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint_reports_infrastructure_status() -> None:
    response = TestClient(app).get("/api/health")

    assert response.status_code == 200
    assert set(response.json()) == {"api", "database", "blockchain"}
    assert response.json()["api"] == "healthy"
    assert response.json()["blockchain"] == "unavailable"
