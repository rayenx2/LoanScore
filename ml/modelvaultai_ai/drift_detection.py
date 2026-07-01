from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import joblib
import pandas as pd

from modelvaultai_ai.feature_engineering import add_credit_risk_features
from modelvaultai_ai.prediction import DEFAULT_MODEL_PATH, classify_risk, load_risk_thresholds

try:
    from scipy.stats import ks_2samp
except ImportError:  # pragma: no cover
    ks_2samp = None


DEFAULT_BASELINE_PATH = Path("data/sample_data/credit_risk_sample.csv")
DEFAULT_PRODUCTION_PATH = Path("data/sample_data/credit_risk_production.csv")
NUMERIC_FEATURES = [
    "age",
    "income",
    "credit_score",
    "loan_amount",
    "loan_term_months",
    "employment_years",
    "debt_to_income_ratio",
    "previous_defaults",
    "number_of_open_accounts",
]
CATEGORICAL_FEATURES = ["loan_purpose"]
IMPORTANT_FEATURES = {"credit_score", "loan_amount", "debt_to_income_ratio", "previous_defaults"}


def compute_population_stability_index(expected: list[float], actual: list[float]) -> float:
    if len(expected) != len(actual):
        raise ValueError("Expected and actual distributions must have the same length.")

    psi = 0.0
    for expected_pct, actual_pct in zip(expected, actual, strict=True):
        expected_pct = max(expected_pct, 1e-6)
        actual_pct = max(actual_pct, 1e-6)
        psi += (actual_pct - expected_pct) * __import__("math").log(actual_pct / expected_pct)
    return round(psi, 4)


def drift_status(score: float) -> str:
    if score >= 0.2:
        return "drift"
    if score >= 0.1:
        return "watch"
    return "stable"


def _numeric_status(abs_percentage_change: float, ks_p_value: float | None) -> str:
    if abs_percentage_change >= 0.25 or (ks_p_value is not None and ks_p_value < 0.01):
        return "high"
    if abs_percentage_change >= 0.1 or (ks_p_value is not None and ks_p_value < 0.05):
        return "medium"
    return "low"


def _categorical_status(distribution_change: float) -> str:
    if distribution_change >= 0.25:
        return "high"
    if distribution_change >= 0.1:
        return "medium"
    return "low"


def _risk_summary(dataframe: pd.DataFrame, model_path: Path = DEFAULT_MODEL_PATH) -> dict[str, Any]:
    risk_counts = {"Low": 0, "Medium": 0, "High": 0}
    model = joblib.load(model_path)
    thresholds = load_risk_thresholds(model_path.parent / "metrics.json")
    features = add_credit_risk_features(dataframe.drop(columns=["defaulted"], errors="ignore"))
    probabilities = [float(value) for value in model.predict_proba(features)[:, 1]]

    for probability in probabilities:
        risk_counts[classify_risk(probability, thresholds=thresholds)] += 1

    total = max(len(dataframe), 1)
    return {
        "total_records": int(len(dataframe)),
        "average_default_probability": round(sum(probabilities) / max(len(probabilities), 1), 4),
        "low_risk_percentage": round(risk_counts["Low"] / total, 4),
        "medium_risk_percentage": round(risk_counts["Medium"] / total, 4),
        "high_risk_percentage": round(risk_counts["High"] / total, 4),
    }


def detect_numeric_drift(baseline: pd.DataFrame, production: pd.DataFrame) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for feature in NUMERIC_FEATURES:
        if feature not in baseline.columns or feature not in production.columns:
            continue

        baseline_values = baseline[feature].dropna()
        production_values = production[feature].dropna()
        baseline_mean = float(baseline_values.mean())
        production_mean = float(production_values.mean())
        mean_difference = production_mean - baseline_mean
        percentage_change = mean_difference / abs(baseline_mean) if baseline_mean else 0.0
        ks_p_value = None
        if ks_2samp is not None:
            ks_p_value = float(ks_2samp(baseline_values, production_values).pvalue)

        status = _numeric_status(abs(percentage_change), ks_p_value)
        details.append(
            {
                "feature_name": feature,
                "feature_type": "numeric",
                "baseline_mean": round(baseline_mean, 4),
                "production_mean": round(production_mean, 4),
                "mean_difference": round(mean_difference, 4),
                "percentage_change": round(percentage_change, 4),
                "ks_p_value": round(ks_p_value, 6) if ks_p_value is not None else None,
                "distribution_change": None,
                "status": status,
                "important": feature in IMPORTANT_FEATURES,
            }
        )
    return details


def detect_categorical_drift(baseline: pd.DataFrame, production: pd.DataFrame) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for feature in CATEGORICAL_FEATURES:
        if feature not in baseline.columns or feature not in production.columns:
            continue

        baseline_dist = baseline[feature].value_counts(normalize=True)
        production_dist = production[feature].value_counts(normalize=True)
        categories = sorted(set(baseline_dist.index).union(set(production_dist.index)))
        distribution_change = sum(
            abs(float(production_dist.get(category, 0.0)) - float(baseline_dist.get(category, 0.0)))
            for category in categories
        ) / 2

        details.append(
            {
                "feature_name": feature,
                "feature_type": "categorical",
                "baseline_mean": None,
                "production_mean": None,
                "mean_difference": None,
                "percentage_change": None,
                "ks_p_value": None,
                "distribution_change": round(distribution_change, 4),
                "status": _categorical_status(distribution_change),
                "important": feature in IMPORTANT_FEATURES,
            }
        )
    return details


def calculate_performance_drop(baseline: pd.DataFrame, production: pd.DataFrame) -> float | None:
    if "defaulted" not in baseline.columns or "defaulted" not in production.columns:
        return None

    baseline_default_rate = float(baseline["defaulted"].mean())
    production_default_rate = float(production["defaulted"].mean())
    return round(max(production_default_rate - baseline_default_rate, 0.0), 4)


def calculate_model_health_score(
    drift_details: list[dict[str, Any]],
    performance_drop: float | None,
    risk_summary: dict[str, Any],
    baseline_risk_summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    high_count = sum(1 for detail in drift_details if detail["status"] == "high")
    medium_count = sum(1 for detail in drift_details if detail["status"] == "medium")
    high_risk_increase = 0.0
    if baseline_risk_summary:
        high_risk_increase = max(
            float(risk_summary["high_risk_percentage"]) - float(baseline_risk_summary["high_risk_percentage"]),
            0.0,
        )

    score = 100 - (high_count * 12) - (medium_count * 5) - int((performance_drop or 0) * 100) - int(high_risk_increase * 100)
    score = max(0, min(100, score))
    status = "Healthy"
    if score < 60:
        status = "Critical"
    elif score < 80:
        status = "Warning"

    return {
        "score": int(score),
        "status": status,
        "high_drift_features": high_count,
        "medium_drift_features": medium_count,
        "performance_drop": performance_drop,
        "high_risk_increase": round(high_risk_increase, 4),
    }


def generate_drift_report(
    baseline_path: Path = DEFAULT_BASELINE_PATH,
    production_path: Path = DEFAULT_PRODUCTION_PATH,
    model_path: Path = DEFAULT_MODEL_PATH,
) -> dict[str, Any]:
    baseline = pd.read_csv(baseline_path)
    production = pd.read_csv(production_path)

    drift_details = detect_numeric_drift(baseline, production) + detect_categorical_drift(baseline, production)
    drift_summary = {
        "total_features": len(drift_details),
        "high_drift_features": sum(1 for detail in drift_details if detail["status"] == "high"),
        "medium_drift_features": sum(1 for detail in drift_details if detail["status"] == "medium"),
        "low_drift_features": sum(1 for detail in drift_details if detail["status"] == "low"),
    }
    production_risk_summary = _risk_summary(production, model_path=model_path)
    baseline_risk_summary = _risk_summary(baseline, model_path=model_path)
    performance_drop = calculate_performance_drop(baseline, production)
    health = calculate_model_health_score(
        drift_details,
        performance_drop,
        production_risk_summary,
        baseline_risk_summary,
    )

    return {
        "baseline_dataset": str(baseline_path),
        "production_dataset": str(production_path),
        "drift_detected": drift_summary["high_drift_features"] > 0 or drift_summary["medium_drift_features"] > 0,
        "drift_summary": drift_summary,
        "features": drift_details,
        "model_health": health,
        "risk_summary": production_risk_summary,
        "baseline_risk_summary": baseline_risk_summary,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run LoanScore drift detection.")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE_PATH)
    parser.add_argument("--production", type=Path, default=DEFAULT_PRODUCTION_PATH)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    args = parser.parse_args()

    report = generate_drift_report(
        baseline_path=args.baseline,
        production_path=args.production,
        model_path=args.model,
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
