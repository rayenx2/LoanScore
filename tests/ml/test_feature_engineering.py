import pandas as pd

from modelvaultai_ai.feature_engineering import add_credit_risk_features, credit_score_band, income_band


def test_credit_score_and_income_bands() -> None:
    assert credit_score_band(760) == "excellent"
    assert credit_score_band(640) == "fair"
    assert income_band(130000) == "high"
    assert income_band(42000) == "moderate"


def test_add_credit_risk_features() -> None:
    dataframe = pd.DataFrame(
        [
            {
                "age": 44,
                "income": 50000,
                "credit_score": 600,
                "loan_amount": 30000,
                "loan_term_months": 60,
                "employment_years": 3,
                "debt_to_income_ratio": 0.42,
                "previous_defaults": 1,
                "number_of_open_accounts": 9,
                "loan_purpose": "medical",
                "defaulted": 1,
            }
        ]
    )

    engineered = add_credit_risk_features(dataframe)

    assert engineered.loc[0, "loan_to_income_ratio"] == 0.6
    assert engineered.loc[0, "credit_score_band"] == "fair"
    assert engineered.loc[0, "risk_band"] in {"low", "medium", "high"}
