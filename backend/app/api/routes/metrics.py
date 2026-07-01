from fastapi import APIRouter

from app.schemas.metrics import MetricsHistoryResponse, ModelMetricsResponse
from app.services.metrics_service import get_metrics_history, get_model_metrics


router = APIRouter()


@router.get("/metrics", response_model=ModelMetricsResponse)
def model_metrics() -> ModelMetricsResponse:
    return get_model_metrics()


@router.get("/model-metrics", response_model=ModelMetricsResponse)
def model_metrics_alias() -> ModelMetricsResponse:
    return get_model_metrics()


@router.get("/model-metrics/history", response_model=MetricsHistoryResponse)
def model_metrics_history() -> MetricsHistoryResponse:
    return get_metrics_history()
