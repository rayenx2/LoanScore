from modelvaultai_ai.drift_detection import compute_population_stability_index, drift_status


def test_compute_population_stability_index() -> None:
    score = compute_population_stability_index([0.2, 0.3, 0.5], [0.25, 0.25, 0.5])

    assert score >= 0


def test_drift_status() -> None:
    assert drift_status(0.05) == "stable"
    assert drift_status(0.12) == "watch"
    assert drift_status(0.24) == "drift"
