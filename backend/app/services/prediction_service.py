from fastapi import HTTPException, status

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.activity_service import record_prediction
from modelvaultai_ai.model_training import MODEL_VERSION
from modelvaultai_ai.prediction import predict_default_risk


def predict_credit_default(request: PredictionRequest) -> PredictionResponse:
    try:
        prediction = predict_default_risk(request.features.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except (ValueError, KeyError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid applicant features: {exc}",
        ) from exc

    response = PredictionResponse(
        applicant_id=request.applicant_id,
        default_probability=float(prediction["default_probability"]),
        risk_class=str(prediction["risk_class"]),
        reason_codes=list(prediction["reason_codes"]),
        explanation_text=str(prediction["explanation_text"]),
        top_risk_factors=list(prediction["top_risk_factors"]),
        model_version=MODEL_VERSION,
    )

    record_prediction(
        applicant_id=response.applicant_id,
        risk_class=response.risk_class,
        default_probability=response.default_probability,
    )

    return response
