from pydantic import BaseModel

from app.schemas.metrics import ClassificationMetrics


class RetrainingRecommendationRequest(BaseModel):
    baseline_dataset_uri: str = "data/sample_data/credit_risk_sample.csv"
    production_dataset_uri: str = "data/sample_data/credit_risk_production.csv"


class RetrainingRecommendationResponse(BaseModel):
    retraining_needed: bool
    priority: str
    reasons: list[str]
    recommended_action: str


class RetrainingRunResponse(BaseModel):
    promoted: bool
    reason: str
    challenger_model_name: str
    training_rows: int
    champion_metrics: ClassificationMetrics | None
    challenger_metrics: ClassificationMetrics
