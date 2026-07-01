from pydantic import BaseModel


class DriftFeatureDetail(BaseModel):
    feature_name: str
    feature_type: str
    baseline_mean: float | None = None
    production_mean: float | None = None
    mean_difference: float | None = None
    percentage_change: float | None = None
    ks_p_value: float | None = None
    distribution_change: float | None = None
    status: str
    important: bool


class DriftDetectionRequest(BaseModel):
    baseline_dataset_uri: str = "data/sample_data/credit_risk_sample.csv"
    production_dataset_uri: str = "data/sample_data/credit_risk_production.csv"


class DriftSummary(BaseModel):
    total_features: int
    high_drift_features: int
    medium_drift_features: int
    low_drift_features: int


class RiskSummary(BaseModel):
    total_records: int
    average_default_probability: float
    low_risk_percentage: float
    medium_risk_percentage: float
    high_risk_percentage: float


class ModelHealth(BaseModel):
    score: int
    status: str
    high_drift_features: int
    medium_drift_features: int
    performance_drop: float | None = None
    high_risk_increase: float


class DriftDetectionResponse(BaseModel):
    baseline_dataset: str
    production_dataset: str
    drift_detected: bool
    drift_summary: DriftSummary
    features: list[DriftFeatureDetail]


class ModelHealthResponse(BaseModel):
    health: ModelHealth
    drift_summary: DriftSummary
    risk_summary: RiskSummary
