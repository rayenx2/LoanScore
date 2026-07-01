from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone as _tz
UTC = _tz.utc
from pathlib import Path
from typing import Any

from modelvaultai_ai.drift_detection import (
    DEFAULT_BASELINE_PATH,
    DEFAULT_MODEL_PATH,
    DEFAULT_PRODUCTION_PATH,
    generate_drift_report,
)
from modelvaultai_ai.retraining_recommendation import recommend_from_monitoring_report


DEFAULT_METRICS_PATH = Path("ml/artifacts/metrics.json")
DEFAULT_REPORTS_DIR = Path("reports")
DEFAULT_REPORT_JSON_PATH = DEFAULT_REPORTS_DIR / "model_monitoring_report.json"
DEFAULT_REPORT_MD_PATH = DEFAULT_REPORTS_DIR / "model_monitoring_report.md"


def load_model_metrics(metrics_path: Path = DEFAULT_METRICS_PATH) -> dict[str, Any]:
    return json.loads(metrics_path.read_text(encoding="utf-8"))


def _top_drifted_features(features: list[dict[str, Any]], limit: int = 5) -> list[dict[str, Any]]:
    status_rank = {"high": 0, "medium": 1, "low": 2}
    sorted_features = sorted(
        features,
        key=lambda feature: (
            status_rank[str(feature["status"])],
            -abs(float(feature["percentage_change"] or feature["distribution_change"] or 0.0)),
        ),
    )
    return sorted_features[:limit]


def _key_business_risks(report: dict[str, Any], recommendation: dict[str, Any]) -> list[str]:
    risks: list[str] = []
    health = report["model_health"]
    risk_summary = report["risk_summary"]

    if health["status"] == "Critical":
        risks.append("Model reliability is critical and should be reviewed before expanding automated use.")
    elif health["status"] == "Warning":
        risks.append("Model reliability is showing early warning signs and should be monitored closely.")

    if float(risk_summary["high_risk_percentage"]) >= 0.3:
        risks.append("A large share of production applicants is being classified as high risk.")

    if report["drift_summary"]["high_drift_features"] > 0:
        risks.append("Important borrower characteristics have shifted from the training baseline.")

    if recommendation["retraining_needed"]:
        risks.append("Retraining is recommended before treating the current model as stable.")

    return risks or ["No major business risks are currently active."]


def _recommended_next_steps(report: dict[str, Any], recommendation: dict[str, Any]) -> list[str]:
    if recommendation["retraining_needed"]:
        return [
            "Review high-drift features with credit risk and data owners.",
            "Create a retraining dataset from recent production records.",
            "Train challenger models and compare fairness, recall, precision, and ROC-AUC.",
            "Keep enhanced monitoring active until production data stabilizes.",
        ]

    if report["model_health"]["status"] == "Warning":
        return [
            "Continue weekly monitoring of drift and high-risk prediction share.",
            "Prepare a retraining plan if drift worsens or labels confirm performance degradation.",
        ]

    return [
        "Continue routine monitoring.",
        "Refresh the report after the next production scoring window.",
    ]


def build_monitoring_report(
    baseline_path: Path = DEFAULT_BASELINE_PATH,
    production_path: Path = DEFAULT_PRODUCTION_PATH,
    model_path: Path = DEFAULT_MODEL_PATH,
    metrics_path: Path = DEFAULT_METRICS_PATH,
) -> dict[str, Any]:
    metrics = load_model_metrics(metrics_path)
    drift_report = generate_drift_report(
        baseline_path=baseline_path,
        production_path=production_path,
        model_path=model_path,
    )
    recommendation = recommend_from_monitoring_report(drift_report)
    top_drifted_features = _top_drifted_features(drift_report["features"])
    key_business_risks = _key_business_risks(drift_report, recommendation)
    recommended_next_steps = _recommended_next_steps(drift_report, recommendation)

    health = drift_report["model_health"]
    high_risk_percentage = drift_report["risk_summary"]["high_risk_percentage"]
    executive_summary = (
        f"Model health is {health['status']} with a score of {health['score']}/100. "
        f"{drift_report['drift_summary']['high_drift_features']} features show high drift, "
        f"and {high_risk_percentage:.1%} of production applicants are predicted high risk. "
        f"Retraining priority is {recommendation['priority']}."
    )

    return {
        "generated_at": datetime.now(UTC).isoformat(),
        "executive_summary": executive_summary,
        "model_status": health["status"],
        "model_health_score": health["score"],
        "model_metrics": metrics,
        "drift_summary": drift_report["drift_summary"],
        "model_health": health,
        "risk_summary": drift_report["risk_summary"],
        "high_risk_prediction_percentage": high_risk_percentage,
        "top_drifted_features": top_drifted_features,
        "retraining_recommendation": recommendation,
        "key_business_risks": key_business_risks,
        "recommended_next_steps": recommended_next_steps,
    }


def render_markdown_report(report: dict[str, Any]) -> str:
    top_features = "\n".join(
        f"- {feature['feature_name']}: {feature['status']} drift"
        for feature in report["top_drifted_features"]
    )
    risks = "\n".join(f"- {risk}" for risk in report["key_business_risks"])
    steps = "\n".join(f"- {step}" for step in report["recommended_next_steps"])
    recommendation = report["retraining_recommendation"]

    return f"""# LoanScore Monitoring Report

Generated at: {report['generated_at']}

## Executive Summary

{report['executive_summary']}

## Model Status

- Status: {report['model_status']}
- Health score: {report['model_health_score']}/100
- High-risk prediction percentage: {report['high_risk_prediction_percentage']:.1%}

## Drift Summary

- High drift features: {report['drift_summary']['high_drift_features']}
- Medium drift features: {report['drift_summary']['medium_drift_features']}
- Low drift features: {report['drift_summary']['low_drift_features']}

## Top Drifted Features

{top_features}

## Retraining Recommendation

- Retraining needed: {recommendation['retraining_needed']}
- Priority: {recommendation['priority']}
- Recommended action: {recommendation['recommended_action']}

## Key Business Risks

{risks}

## Recommended Next Steps

{steps}
"""


def save_monitoring_report(
    report: dict[str, Any],
    json_path: Path = DEFAULT_REPORT_JSON_PATH,
    markdown_path: Path = DEFAULT_REPORT_MD_PATH,
) -> dict[str, Any]:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    markdown_path.write_text(render_markdown_report(report), encoding="utf-8")
    return report


def generate_and_save_monitoring_report(
    baseline_path: Path = DEFAULT_BASELINE_PATH,
    production_path: Path = DEFAULT_PRODUCTION_PATH,
    model_path: Path = DEFAULT_MODEL_PATH,
    metrics_path: Path = DEFAULT_METRICS_PATH,
    json_path: Path = DEFAULT_REPORT_JSON_PATH,
    markdown_path: Path = DEFAULT_REPORT_MD_PATH,
) -> dict[str, Any]:
    report = build_monitoring_report(
        baseline_path=baseline_path,
        production_path=production_path,
        model_path=model_path,
        metrics_path=metrics_path,
    )
    return save_monitoring_report(report, json_path=json_path, markdown_path=markdown_path)


def load_latest_monitoring_report(
    json_path: Path = DEFAULT_REPORT_JSON_PATH,
) -> dict[str, Any]:
    if not json_path.exists():
        return generate_and_save_monitoring_report(json_path=json_path)
    return json.loads(json_path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a LoanScore monitoring report.")
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE_PATH)
    parser.add_argument("--production", type=Path, default=DEFAULT_PRODUCTION_PATH)
    parser.add_argument("--model", type=Path, default=DEFAULT_MODEL_PATH)
    parser.add_argument("--metrics", type=Path, default=DEFAULT_METRICS_PATH)
    parser.add_argument("--json-output", type=Path, default=DEFAULT_REPORT_JSON_PATH)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_REPORT_MD_PATH)
    args = parser.parse_args()

    report = generate_and_save_monitoring_report(
        baseline_path=args.baseline,
        production_path=args.production,
        model_path=args.model,
        metrics_path=args.metrics,
        json_path=args.json_output,
        markdown_path=args.markdown_output,
    )
    print(f"Generated monitoring report with status {report['model_status']} at {args.json_output}")


if __name__ == "__main__":
    main()
