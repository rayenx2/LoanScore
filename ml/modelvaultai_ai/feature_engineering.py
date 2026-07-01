from __future__ import annotations

import pandas as pd


def calculate_debt_to_income_ratio(total_monthly_debt: float, monthly_income: float) -> float:
    if monthly_income <= 0:
        return 0.0
    return round(total_monthly_debt / monthly_income, 4)


def credit_score_band(score: float) -> str:
    if score >= 740:
        return "excellent"
    if score >= 670:
        return "good"
    if score >= 580:
        return "fair"
    return "poor"


def income_band(income: float) -> str:
    if income >= 120000:
        return "high"
    if income >= 65000:
        return "middle"
    if income >= 35000:
        return "moderate"
    return "low"


def risk_band(row: pd.Series | dict[str, float]) -> str:
    credit_score = float(row["credit_score"])
    debt_to_income = float(row["debt_to_income_ratio"])
    previous_defaults = int(row["previous_defaults"])
    loan_to_income = float(row["loan_to_income_ratio"])

    risk_points = 0
    risk_points += 2 if credit_score < 580 else 1 if credit_score < 670 else 0
    risk_points += 2 if debt_to_income >= 0.5 else 1 if debt_to_income >= 0.36 else 0
    risk_points += 2 if loan_to_income >= 0.8 else 1 if loan_to_income >= 0.45 else 0
    risk_points += min(previous_defaults, 2)

    if risk_points >= 5:
        return "high"
    if risk_points >= 2:
        return "medium"
    return "low"


def add_credit_risk_features(dataframe: pd.DataFrame) -> pd.DataFrame:
    data = dataframe.copy()
    data["loan_to_income_ratio"] = data["loan_amount"] / data["income"].clip(lower=1)
    data["credit_score_band"] = data["credit_score"].apply(credit_score_band)
    data["income_band"] = data["income"].apply(income_band)
    data["risk_band"] = data.apply(risk_band, axis=1)
    return data


def create_credit_risk_features(record: dict[str, float | int | str]) -> dict[str, float | int | str]:
    dataframe = pd.DataFrame([record])
    return add_credit_risk_features(dataframe).iloc[0].to_dict()
