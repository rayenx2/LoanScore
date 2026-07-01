from fastapi import APIRouter

from app.schemas.retraining import (
    RetrainingRecommendationRequest,
    RetrainingRecommendationResponse,
    RetrainingRunResponse,
)
from app.services.retraining_service import recommend_retraining, run_retraining


router = APIRouter()


@router.post("/retraining/recommendation", response_model=RetrainingRecommendationResponse)
def retraining_recommendation(
    request: RetrainingRecommendationRequest,
) -> RetrainingRecommendationResponse:
    return recommend_retraining(request)


@router.get("/retraining-recommendation", response_model=RetrainingRecommendationResponse)
def retraining_recommendation_default() -> RetrainingRecommendationResponse:
    return recommend_retraining(RetrainingRecommendationRequest())


@router.post("/retraining-recommendation", response_model=RetrainingRecommendationResponse)
def retraining_recommendation_alias(
    request: RetrainingRecommendationRequest,
) -> RetrainingRecommendationResponse:
    return recommend_retraining(request)


@router.post("/retraining/run", response_model=RetrainingRunResponse)
def retraining_run() -> RetrainingRunResponse:
    """Actually retrains a challenger on baseline+production data and promotes it
    only if it beats the current champion model. Not a blind overwrite."""
    return run_retraining(RetrainingRecommendationRequest())
