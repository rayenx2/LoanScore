from __future__ import annotations

from typing import Any


def top_feature_contributions(contributions: dict[str, float], limit: int = 5) -> list[tuple[str, float]]:
    return sorted(contributions.items(), key=lambda item: abs(item[1]), reverse=True)[:limit]


def _clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def feature_risk_scores(features: dict[str, float | int | str]) -> dict[str, dict[str, Any]]:
    """
    Continuous (0-1) risk contribution per feature, instead of hard boolean
    thresholds. A feature can contribute *some* risk without crossing an
    arbitrary cutoff — this is what lets the explanation stay consistent with
    the model's actual predicted probability instead of silently disagreeing
    with it (e.g. model says Medium risk, old logic said "no risk factors").
    """
    income = max(float(features["income"]), 1.0)
    loan_to_income = float(features["loan_amount"]) / income
    credit_score = float(features["credit_score"])
    debt_to_income_ratio = float(features["debt_to_income_ratio"])
    previous_defaults = int(features["previous_defaults"])
    employment_years = float(features["employment_years"])

    return {
        "credit_score": {
            "value": credit_score,
            "risk_score": _clamp((700 - credit_score) / 400),
            "message": "Low credit score increased the risk.",
        },
        "debt_to_income_ratio": {
            "value": round(debt_to_income_ratio, 4),
            "risk_score": _clamp((debt_to_income_ratio - 0.2) / 0.5),
            "message": "High debt-to-income ratio increased the risk.",
        },
        "previous_defaults": {
            "value": previous_defaults,
            "risk_score": _clamp(previous_defaults / 2),
            "message": "Previous defaults increased the risk.",
        },
        "loan_to_income_ratio": {
            "value": round(loan_to_income, 4),
            "risk_score": _clamp((loan_to_income - 0.2) / 0.6),
            "message": "High loan amount compared to income increased the risk.",
        },
        "employment_years": {
            "value": employment_years,
            "risk_score": _clamp((5 - employment_years) / 5),
            "message": "Short employment history increased the risk.",
        },
    }


def _severity(risk_score: float) -> str:
    if risk_score >= 0.6:
        return "high"
    if risk_score >= 0.3:
        return "medium"
    return "low"


def build_top_risk_factors(
    features: dict[str, float | int | str],
    risk_class: str | None = None,
) -> list[dict[str, Any]]:
    scores = feature_risk_scores(features)
    ranked = sorted(scores.items(), key=lambda item: item[1]["risk_score"], reverse=True)

    factors: list[dict[str, Any]] = [
        {
            "factor": name,
            "severity": _severity(info["risk_score"]),
            "value": info["value"],
            "message": info["message"],
        }
        for name, info in ranked
        if info["risk_score"] >= 0.25
    ]

    # No individual factor crosses a real threshold, but the model's own
    # risk_class says this applicant isn't Low risk anyway — don't falsely
    # claim a clean profile. Surface an explicit "combined risk" factor
    # instead of mislabeling one weak feature's severity to force agreement.
    if not factors and risk_class is not None and risk_class != "Low":
        factors.append(
            {
                "factor": "combined_profile",
                "severity": "medium" if risk_class == "Medium" else "high",
                "value": None,
                "message": (
                    "No single factor crosses a high-risk threshold on its own, but the model's "
                    "combined assessment of this applicant's profile is elevated."
                ),
            }
        )

    if not factors:
        factors.append(
            {
                "factor": "overall_profile",
                "severity": "low",
                "value": None,
                "message": "No major risk factors were detected in this applicant profile.",
            }
        )

    severity_rank = {"high": 0, "medium": 1, "low": 2}
    return sorted(factors, key=lambda factor: severity_rank[str(factor["severity"])])[:5]


def explain_risk_class(
    risk_class: str,
    default_probability: float,
    features: dict[str, float | int | str],
) -> str:
    percent = round(default_probability * 100, 1)
    factors = build_top_risk_factors(features, risk_class=risk_class)
    factor_messages = [factor["message"] for factor in factors if factor["factor"] != "overall_profile"]

    if risk_class == "High":
        opening = f"This applicant is classified as High risk with an estimated {percent}% probability of default."
    elif risk_class == "Medium":
        opening = f"This applicant is classified as Medium risk with an estimated {percent}% probability of default."
    else:
        opening = f"This applicant is classified as Low risk with an estimated {percent}% probability of default."

    if factor_messages:
        return f"{opening} " + " ".join(factor_messages)
    return f"{opening} The profile does not show major credit, debt, prior-default, or loan-exposure warning signs."
