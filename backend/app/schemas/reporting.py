from typing import Any

from pydantic import BaseModel


class ReportFeature(BaseModel):
    feature_name: str
    feature_type: str
    status: str
    important: bool
    percentage_change: float | None = None
    distribution_change: float | None = None
    ks_p_value: float | None = None


class ReportRecommendation(BaseModel):
    retraining_needed: bool
    priority: str
    reasons: list[str]
    recommended_action: str


class MonitoringReportResponse(BaseModel):
    generated_at: str
    executive_summary: str
    model_status: str
    model_health_score: int
    model_metrics: dict[str, Any]
    drift_summary: dict[str, int]
    model_health: dict[str, Any]
    risk_summary: dict[str, Any]
    high_risk_prediction_percentage: float
    top_drifted_features: list[ReportFeature]
    retraining_recommendation: ReportRecommendation
    key_business_risks: list[str]
    recommended_next_steps: list[str]
