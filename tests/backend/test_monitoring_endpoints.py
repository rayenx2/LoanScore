from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_drift_endpoint() -> None:
    response = client.post("/api/v1/drift", json={})

    body = response.json()
    assert response.status_code == 200
    assert body["drift_detected"] is True
    assert body["drift_summary"]["total_features"] == len(body["features"])


def test_model_health_endpoint() -> None:
    response = client.get("/api/v1/model-health")

    body = response.json()
    assert response.status_code == 200
    assert 0 <= body["health"]["score"] <= 100
    assert body["health"]["status"] in {"Healthy", "Warning", "Critical"}


def test_retraining_recommendation_endpoint() -> None:
    response = client.get("/api/v1/retraining-recommendation")

    body = response.json()
    assert response.status_code == 200
    assert set(body) == {
        "retraining_needed",
        "priority",
        "reasons",
        "recommended_action",
    }
