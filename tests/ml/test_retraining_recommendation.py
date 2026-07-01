from modelvaultai_ai.retraining_recommendation import retraining_priority, should_retrain


def test_should_retrain_when_drift_is_high() -> None:
    assert should_retrain(drift_score=0.25, performance_drop=0.01, days_since_training=15)


def test_retraining_priority() -> None:
    assert retraining_priority(drift_score=0.25, performance_drop=0.08) == "high"
