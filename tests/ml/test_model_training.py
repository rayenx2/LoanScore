import json
from pathlib import Path

from modelvaultai_ai.model_training import train_credit_risk_model


def test_model_training_creates_model_and_metrics() -> None:
    artifacts_dir = Path("ml/artifacts/test_model_training")
    summary = train_credit_risk_model(artifacts_dir=artifacts_dir)
    metrics = json.loads(summary.metrics_path.read_text(encoding="utf-8"))

    assert summary.model_path.exists()
    assert (artifacts_dir / "preprocessor.pkl").exists()
    assert summary.metrics_path.exists()
    assert summary.selected_model in {"logistic_regression", "random_forest"}
    assert "roc_auc" in metrics["models"][summary.selected_model]
