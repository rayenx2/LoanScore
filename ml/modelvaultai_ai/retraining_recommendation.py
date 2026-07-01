from __future__ import annotations

from typing import Any


IMPORTANT_FEATURES = {"credit_score", "loan_amount", "debt_to_income_ratio", "previous_defaults"}


def should_retrain(drift_score: float, performance_drop: float, days_since_training: int) -> bool:
    return drift_score >= 0.2 or performance_drop >= 0.05 or days_since_training >= 90


def retraining_priority(drift_score: float, performance_drop: float) -> str:
    if drift_score >= 0.2 and performance_drop >= 0.05:
        return "high"
    if drift_score >= 0.2 or performance_drop >= 0.05:
        return "medium"
    return "low"


def recommend_from_monitoring_report(report: dict[str, Any]) -> dict[str, Any]:
    features = report["features"]
    health = report["model_health"]
    risk_summary = report["risk_summary"]
    baseline_risk_summary = report.get("baseline_risk_summary", {})

    high_drift_important = [
        feature["feature_name"]
        for feature in features
        if feature["status"] == "high" and feature["feature_name"] in IMPORTANT_FEATURES
    ]
    high_risk_increase = max(
        float(risk_summary["high_risk_percentage"]) - float(baseline_risk_summary.get("high_risk_percentage", 0.0)),
        0.0,
    )

    reasons: list[str] = []
    if high_drift_important:
        reasons.append(f"High drift detected in important features: {', '.join(high_drift_important)}.")
    if int(health["score"]) < 75:
        reasons.append(f"Model health score is below threshold at {health['score']}.")
    if high_risk_increase >= 0.1:
        reasons.append(f"Predicted high-risk customer share increased by {high_risk_increase:.1%}.")
    if health.get("performance_drop") is not None and float(health["performance_drop"]) >= 0.05:
        reasons.append(f"Observed default rate increased by {float(health['performance_drop']):.1%}.")

    retraining_needed = bool(reasons)
    if int(health["score"]) < 60 or len(high_drift_important) >= 2:
        priority = "High"
    elif retraining_needed:
        priority = "Medium"
    else:
        priority = "Low"

    recommended_action = (
        "Start retraining analysis with the latest production data and compare challenger models."
        if retraining_needed
        else "Continue monitoring. No retraining trigger is currently active."
    )

    return {
        "retraining_needed": retraining_needed,
        "priority": priority,
        "reasons": reasons or ["No retraining trigger is currently active."],
        "recommended_action": recommended_action,
    }
