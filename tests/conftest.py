from pathlib import Path

import pytest

from modelvaultai_ai.model_training import train_credit_risk_model


@pytest.fixture(scope="session", autouse=True)
def ensure_default_artifacts() -> None:
    model_path = Path("ml/artifacts/model.pkl")
    metrics_path = Path("ml/artifacts/metrics.json")
    if not model_path.exists() or not metrics_path.exists():
        train_credit_risk_model()
