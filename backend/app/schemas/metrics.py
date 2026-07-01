from pydantic import BaseModel


class CurvePoint(BaseModel):
    x: float
    y: float


class ClassificationMetrics(BaseModel):
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    confusion_matrix: list[list[int]]
    roc_curve: list[CurvePoint] = []
    pr_curve: list[CurvePoint] = []


class ModelMetricsResponse(BaseModel):
    model_version: str
    selected_model: str
    selection_metric: str
    training_rows: int
    test_rows: int
    models: dict[str, ClassificationMetrics]


class MetricsHistoryEntry(BaseModel):
    timestamp: str
    selected_model: str
    training_rows: int
    test_rows: int | None = None
    roc_auc: float
    f1_score: float
    accuracy: float
    event: str = "training_run"
    promoted: bool | None = None


class MetricsHistoryResponse(BaseModel):
    history: list[MetricsHistoryEntry]
