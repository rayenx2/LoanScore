from pathlib import Path

from modelvaultai_ai.model_training import train_credit_risk_model
from modelvaultai_ai.prediction import predict_default_risk


def test_prediction_response_shape() -> None:
    artifacts_dir = Path("ml/artifacts/test_prediction")
    summary = train_credit_risk_model(artifacts_dir=artifacts_dir)

    prediction = predict_default_risk(
        {
            "age": 39,
            "income": 68000,
            "credit_score": 650,
            "loan_amount": 28000,
            "loan_term_months": 60,
            "employment_years": 5,
            "debt_to_income_ratio": 0.38,
            "previous_defaults": 0,
            "number_of_open_accounts": 8,
            "loan_purpose": "debt_consolidation",
        },
        model_path=summary.model_path,
    )

    assert 0 <= prediction["default_probability"] <= 1
    assert prediction["risk_class"] in {"Low", "Medium", "High"}
    assert isinstance(prediction["reason_codes"], list)
    assert prediction["explanation_text"]
    assert isinstance(prediction["top_risk_factors"], list)
