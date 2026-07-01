from modelvaultai_ai.explainability import build_top_risk_factors, explain_risk_class


def test_explainability_returns_business_friendly_risk_factors() -> None:
    features = {
        "age": 42,
        "income": 48000,
        "credit_score": 575,
        "loan_amount": 42000,
        "loan_term_months": 60,
        "employment_years": 1,
        "debt_to_income_ratio": 0.52,
        "previous_defaults": 1,
        "number_of_open_accounts": 11,
        "loan_purpose": "debt_consolidation",
    }

    factors = build_top_risk_factors(features)
    explanation = explain_risk_class("High", 0.72, features)

    assert factors[0]["severity"] == "high"
    assert any(factor["factor"] == "credit_score" for factor in factors)
    assert "Low credit score increased the risk." in explanation
    assert "Previous defaults increased the risk." in explanation
