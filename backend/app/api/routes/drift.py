from fastapi import APIRouter

from app.schemas.drift import DriftDetectionRequest, DriftDetectionResponse, ModelHealthResponse
from app.services.drift_service import detect_drift, get_model_health


router = APIRouter()


@router.post("/drift", response_model=DriftDetectionResponse)
def analyze_drift(request: DriftDetectionRequest) -> DriftDetectionResponse:
    return detect_drift(request)


@router.get("/model-health", response_model=ModelHealthResponse)
def model_health() -> ModelHealthResponse:
    return get_model_health(DriftDetectionRequest())
