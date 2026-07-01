from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_monitoring_report_generate_endpoint() -> None:
    response = client.post("/api/v1/monitoring-report/generate")

    body = response.json()
    assert response.status_code == 200
    assert body["executive_summary"]
    assert body["top_drifted_features"]
    assert body["retraining_recommendation"]["priority"] in {"Low", "Medium", "High"}


def test_monitoring_report_get_endpoint() -> None:
    response = client.get("/api/v1/monitoring-report")

    body = response.json()
    assert response.status_code == 200
    assert body["model_status"] in {"Healthy", "Warning", "Critical"}
    assert "key_business_risks" in body
