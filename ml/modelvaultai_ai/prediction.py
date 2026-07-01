from __future__ import annotations

import json
from pathlib import Path

import joblib
import pandas as pd

from modelvaultai_ai.feature_engineering import add_credit_risk_features
from modelvaultai_ai.explainability import build_top_risk_factors, explain_risk_class, feature_risk_scores


DEFAULT_MODEL_PATH = Path("ml/artifacts/model.pkl")
DEFAULT_METRICS_PATH = Path("ml/artifacts/metrics.json")

_REASON_CODE_NAMES = {
    "credit_score": "low_credit_score",
    "debt_to_income_ratio": "high_debt_to_income",
    "previous_defaults": "previous_defaults",
    "loan_to_income_ratio": "high_loan_to_income",
    "employment_years": "short_employment_history",
}

# Fallback only: used if metrics.json has no "risk_thresholds" yet (e.g. a
# model artifact trained before percentile-based thresholds were introduced).
_FALLBACK_THRESHOLDS = {"medium": 0.3, "high": 0.6}


def load_risk_thresholds(metrics_path: Path = DEFAULT_METRICS_PATH) -> dict[str, float]:
    """Risk-class cutoffs are computed at training time from the model's own
    predicted-probability distribution (see model_training._compute_risk_thresholds)
    so "Medium"/"High" always reflect what this specific model actually outputs,
    rather than fixed numbers that assume a distribution it doesn't produce."""
    try:
        payload = json.loads(metrics_path.read_text(encoding="utf-8"))
        thresholds = payload.get("risk_thresholds")
        if thresholds and "medium" in thresholds and "high" in thresholds:
            return {"medium": float(thresholds["medium"]), "high": float(thresholds["high"])}
    except (FileNotFoundError, json.JSONDecodeError, KeyError):
        pass
    return dict(_FALLBACK_THRESHOLDS)


def classify_risk(default_probability: float, thresholds: dict[str, float] | None = None) -> str:
    thresholds = thresholds or _FALLBACK_THRESHOLDS
    if default_probability >= thresholds["high"]:
        return "High"
    if default_probability >= thresholds["medium"]:
        return "Medium"
    return "Low"


def reason_codes(features: dict[str, float | int | str], risk_class: str | None = None) -> list[str]:
    """Reason codes derived from the SAME continuous risk scores used for
    top_risk_factors, so this list can never contradict the model's own
    risk_class (e.g. saying "no_major_risk_flags" while the model says Medium/High)."""
    scores = feature_risk_scores(features)
    ranked = sorted(scores.items(), key=lambda item: item[1]["risk_score"], reverse=True)

    codes = [_REASON_CODE_NAMES[name] for name, info in ranked if info["risk_score"] >= 0.25]

    if not codes and risk_class is not None and risk_class != "Low":
        codes.append("elevated_combined_risk")

    return codes or ["no_major_risk_flags"]


def load_model(model_path: Path = DEFAULT_MODEL_PATH):
    if not model_path.exists():
        raise FileNotFoundError(f"Model artifact not found at {model_path}. Train the model first.")
    return joblib.load(model_path)


def predict_default_risk(
    customer_features: dict[str, float | int | str],
    model_path: Path = DEFAULT_MODEL_PATH,
    metrics_path: Path = DEFAULT_METRICS_PATH,
) -> dict[str, object]:
    model = load_model(model_path)
    dataframe = add_credit_risk_features(pd.DataFrame([customer_features]))
    probability = round(float(model.predict_proba(dataframe)[0][1]), 4)
    risk_class = classify_risk(probability, thresholds=load_risk_thresholds(metrics_path))
    return {
        "default_probability": probability,
        "risk_class": risk_class,
        "reason_codes": reason_codes(customer_features, risk_class=risk_class),
        "explanation_text": explain_risk_class(risk_class, probability, customer_features),
        "top_risk_factors": build_top_risk_factors(customer_features, risk_class=risk_class),
    }
