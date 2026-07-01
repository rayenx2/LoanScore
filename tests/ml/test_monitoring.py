from modelvaultai_ai.drift_detection import generate_drift_report
from modelvaultai_ai.retraining_recommendation import recommend_from_monitoring_report


def test_drift_detection_output_shape() -> None:
    report = generate_drift_report()

    assert "drift_summary" in report
    assert "features" in report
    assert "model_health" in report
    assert "risk_summary" in report
    assert report["drift_summary"]["total_features"] == len(report["features"])


def test_shifted_production_data_detects_high_drift() -> None:
    report = generate_drift_report()

    high_drift_features = [
        feature["feature_name"]
        for feature in report["features"]
        if feature["status"] == "high"
    ]
    # The production dataset applies a documented drift simulation to exactly
    # these 5 feature columns (see scripts/build_credit_risk_dataset.py) —
    # credit_score is deliberately NOT perturbed, so it should stay low-drift.
    assert "debt_to_income_ratio" in high_drift_features
    assert "loan_amount" in high_drift_features
    assert "credit_score" not in high_drift_features
    assert report["drift_detected"]


def test_model_health_score_is_between_zero_and_one_hundred() -> None:
    report = generate_drift_report()

    assert 0 <= report["model_health"]["score"] <= 100
    assert report["model_health"]["status"] in {"Healthy", "Warning", "Critical"}


def test_retraining_recommendation_returns_expected_fields() -> None:
    recommendation = recommend_from_monitoring_report(generate_drift_report())

    assert set(recommendation) == {
        "retraining_needed",
        "priority",
        "reasons",
        "recommended_action",
    }
    assert recommendation["priority"] in {"Low", "Medium", "High"}
    assert isinstance(recommendation["reasons"], list)
