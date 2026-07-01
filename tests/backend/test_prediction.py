from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_prediction_endpoint_returns_risk_score() -> None:
    response = client.post(
        "/api/v1/predict",
        json={
            "applicant_id": "applicant-001",
            "features": {
                "age": 38,
                "income": 72000,
                "credit_score": 680,
                "loan_amount": 22000,
                "loan_term_months": 60,
                "employment_years": 4,
                "debt_to_income_ratio": 0.32,
                "previous_defaults": 0,
                "number_of_open_accounts": 7,
                "loan_purpose": "auto",
            },
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["applicant_id"] == "applicant-001"
    assert 0 <= body["default_probability"] <= 1
    assert body["risk_class"] in {"Low", "Medium", "High"}
    assert isinstance(body["reason_codes"], list)
    assert body["explanation_text"]
    assert isinstance(body["top_risk_factors"], list)
