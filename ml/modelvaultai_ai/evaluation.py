from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def _downsample(points: list[tuple[float, float]], max_points: int = 25) -> list[dict[str, float]]:
    if len(points) <= max_points:
        indices = range(len(points))
    else:
        indices = np.linspace(0, len(points) - 1, max_points).round().astype(int)
    return [{"x": round(float(points[i][0]), 4), "y": round(float(points[i][1]), 4)} for i in indices]


def evaluate_classifier(y_true, y_pred, y_probability) -> dict[str, object]:
    fpr, tpr, _ = roc_curve(y_true, y_probability)
    precision_points, recall_points, _ = precision_recall_curve(y_true, y_probability)

    return {
        "accuracy": round(float(accuracy_score(y_true, y_pred)), 4),
        "precision": round(float(precision_score(y_true, y_pred, zero_division=0)), 4),
        "recall": round(float(recall_score(y_true, y_pred, zero_division=0)), 4),
        "f1_score": round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
        "roc_auc": round(float(roc_auc_score(y_true, y_probability)), 4),
        "confusion_matrix": confusion_matrix(y_true, y_pred).tolist(),
        "roc_curve": _downsample(list(zip(fpr, tpr))),
        "pr_curve": _downsample(list(zip(recall_points, precision_points))),
    }


def summarize_classification_metrics(metrics: dict[str, float]) -> dict[str, str]:
    thresholds = {"roc_auc": 0.78, "precision": 0.65, "recall": 0.7, "f1_score": 0.6}
    return {name: "healthy" if value >= thresholds.get(name, 0.0) else "watch" for name, value in metrics.items()}
