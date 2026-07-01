from __future__ import annotations

from dataclasses import dataclass

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


TARGET_COLUMN = "defaulted"
BASE_NUMERIC_COLUMNS = [
    "age",
    "income",
    "credit_score",
    "loan_amount",
    "loan_term_months",
    "employment_years",
    "debt_to_income_ratio",
    "previous_defaults",
    "number_of_open_accounts",
    "loan_to_income_ratio",
]
BASE_CATEGORICAL_COLUMNS = ["loan_purpose", "credit_score_band", "income_band", "risk_band"]


@dataclass(frozen=True)
class FeatureSchema:
    numeric_columns: list[str]
    categorical_columns: list[str]
    target_column: str = TARGET_COLUMN


def handle_missing_values(dataframe: pd.DataFrame) -> pd.DataFrame:
    data = dataframe.copy()

    for column in data.select_dtypes(include=["number"]).columns:
        data[column] = data[column].fillna(data[column].median())

    for column in data.select_dtypes(exclude=["number"]).columns:
        mode = data[column].mode(dropna=True)
        fill_value = mode.iloc[0] if not mode.empty else "unknown"
        data[column] = data[column].fillna(fill_value)

    return data


def split_features_target(dataframe: pd.DataFrame, target_column: str = TARGET_COLUMN) -> tuple[pd.DataFrame, pd.Series]:
    if target_column not in dataframe.columns:
        raise ValueError(f"Target column '{target_column}' is missing.")

    features = dataframe.drop(columns=[target_column])
    target = dataframe[target_column].astype(int)
    return features, target


def infer_feature_schema(dataframe: pd.DataFrame) -> FeatureSchema:
    available_numeric = [column for column in BASE_NUMERIC_COLUMNS if column in dataframe.columns]
    available_categorical = [column for column in BASE_CATEGORICAL_COLUMNS if column in dataframe.columns]
    return FeatureSchema(numeric_columns=available_numeric, categorical_columns=available_categorical)


def build_preprocessor(schema: FeatureSchema) -> ColumnTransformer:
    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("numeric", numeric_pipeline, schema.numeric_columns),
            ("categorical", categorical_pipeline, schema.categorical_columns),
        ]
    )


def prepare_modeling_data(dataframe: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, FeatureSchema]:
    clean_data = handle_missing_values(dataframe)
    features, target = split_features_target(clean_data)
    schema = infer_feature_schema(features)
    return features, target, schema
