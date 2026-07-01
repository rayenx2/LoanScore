from pathlib import Path

from app.schemas.retraining import (
    RetrainingRecommendationRequest,
    RetrainingRecommendationResponse,
    RetrainingRunResponse,
)
from app.services.activity_service import record_retraining_run
from modelvaultai_ai.drift_detection import generate_drift_report
from modelvaultai_ai.retraining_pipeline import run_retraining_challenge
from modelvaultai_ai.retraining_recommendation import recommend_from_monitoring_report


def recommend_retraining(
    request: RetrainingRecommendationRequest,
) -> RetrainingRecommendationResponse:
    report = generate_drift_report(
        baseline_path=Path(request.baseline_dataset_uri),
        production_path=Path(request.production_dataset_uri),
    )
    return RetrainingRecommendationResponse(**recommend_from_monitoring_report(report))


def run_retraining(request: RetrainingRecommendationRequest) -> RetrainingRunResponse:
    result = run_retraining_challenge(
        baseline_path=Path(request.baseline_dataset_uri),
        production_path=Path(request.production_dataset_uri),
    )
    record_retraining_run(promoted=result.promoted)
    return RetrainingRunResponse(
        promoted=result.promoted,
        reason=result.reason,
        challenger_model_name=result.challenger_model_name,
        training_rows=result.training_rows,
        champion_metrics=result.champion_metrics,
        challenger_metrics=result.challenger_metrics,
    )
