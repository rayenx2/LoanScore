from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_model_metrics_endpoint() -> None:
    response = client.get("/api/v1/model-metrics")

    body = response.json()
    assert response.status_code == 200
    assert body["selected_model"] in {"logistic_regression", "random_forest"}
    assert "roc_auc" in body["models"][body["selected_model"]]
