from pathlib import Path

from fastapi import HTTPException, status

from app.schemas.drift import DriftDetectionRequest, DriftDetectionResponse, ModelHealthResponse
from app.services.activity_service import record_drift_check, record_model_health
from modelvaultai_ai.drift_detection import generate_drift_report


def _build_report(request: DriftDetectionRequest) -> dict:
    baseline_path = Path(request.baseline_dataset_uri)
    production_path = Path(request.production_dataset_uri)

    if not baseline_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Baseline dataset not found at {baseline_path}.",
        )

    if not production_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Production dataset not found at {production_path}.",
        )

    try:
        return generate_drift_report(baseline_path=baseline_path, production_path=production_path)
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc


def detect_drift(request: DriftDetectionRequest) -> DriftDetectionResponse:
    report = _build_report(request)

    record_drift_check(drift_detected=bool(report["drift_detected"]))

    return DriftDetectionResponse(
        baseline_dataset=report["baseline_dataset"],
        production_dataset=report["production_dataset"],
        drift_detected=report["drift_detected"],
        drift_summary=report["drift_summary"],
        features=report["features"],
    )


def get_model_health(request: DriftDetectionRequest) -> ModelHealthResponse:
    report = _build_report(request)

    record_model_health(score=int(report["model_health"]["score"]))

    return ModelHealthResponse(
        health=report["model_health"],
        drift_summary=report["drift_summary"],
        risk_summary=report["risk_summary"],
    )
