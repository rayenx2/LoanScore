from datetime import datetime

from pydantic import BaseModel


class ActivityEvent(BaseModel):
    timestamp: datetime
    event_type: str
    applicant_id: str | None = None
    risk_class: str | None = None
    default_probability: float | None = None
    drift_detected: bool | None = None
    model_health_score: int | None = None
    promoted: bool | None = None


class ActivitySummary(BaseModel):
    total_predictions: int
    total_drift_checks: int
    total_reports_generated: int
    high_risk_predictions: int
    average_default_probability: float | None = None
    last_drift_detected: bool | None = None
    last_model_health_score: int | None = None


class ActivityResponse(BaseModel):
    summary: ActivitySummary
    recent_events: list[ActivityEvent]
