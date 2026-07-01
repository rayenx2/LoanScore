import pandas as pd

from modelvaultai_ai.feature_engineering import add_credit_risk_features
from modelvaultai_ai.processing import handle_missing_values, prepare_modeling_data, split_features_target


def test_handle_missing_values_fills_numeric_and_categorical_values() -> None:
    dataframe = pd.DataFrame(
        {
            "income": [50000.0, None, 70000.0],
            "loan_purpose": ["auto", None, "medical"],
        }
    )

    clean = handle_missing_values(dataframe)

    assert clean.isna().sum().sum() == 0


def test_split_features_target() -> None:
    dataframe = pd.DataFrame({"income": [50000], "defaulted": [0]})

    features, target = split_features_target(dataframe)

    assert "defaulted" not in features.columns
    assert target.tolist() == [0]


def test_prepare_modeling_data_returns_schema() -> None:
    dataframe = pd.DataFrame(
        {
            "age": [35, 48],
            "income": [70000, 52000],
            "credit_score": [710, 610],
            "loan_amount": [20000, 26000],
            "loan_term_months": [60, 48],
            "employment_years": [6, 2],
            "debt_to_income_ratio": [0.28, 0.45],
            "previous_defaults": [0, 1],
            "number_of_open_accounts": [7, 11],
            "loan_purpose": ["auto", "medical"],
            "defaulted": [0, 1],
        }
    )
    engineered = add_credit_risk_features(dataframe)

    features, target, schema = prepare_modeling_data(engineered)

    assert len(features) == 2
    assert target.tolist() == [0, 1]
    assert "loan_to_income_ratio" in schema.numeric_columns
    assert "loan_purpose" in schema.categorical_columns
