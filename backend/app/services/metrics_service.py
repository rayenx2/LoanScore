import json
from pathlib import Path

from fastapi import HTTPException, status

from app.schemas.metrics import MetricsHistoryResponse, ModelMetricsResponse


DEFAULT_METRICS_PATH = Path("ml/artifacts/metrics.json")
DEFAULT_METRICS_HISTORY_PATH = Path("ml/artifacts/metrics_history.json")


def get_model_metrics(metrics_path: Path = DEFAULT_METRICS_PATH) -> ModelMetricsResponse:
    if not metrics_path.exists():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Metrics artifact not found at {metrics_path}. Train the model first.",
        )

    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    return ModelMetricsResponse(**payload)


def get_metrics_history(history_path: Path = DEFAULT_METRICS_HISTORY_PATH) -> MetricsHistoryResponse:
    if not history_path.exists():
        return MetricsHistoryResponse(history=[])
    history = json.loads(history_path.read_text(encoding="utf-8"))
    return MetricsHistoryResponse(history=history)
