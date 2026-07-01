from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from modelvaultai_ai.evaluation import evaluate_classifier
from modelvaultai_ai.feature_engineering import add_credit_risk_features
from modelvaultai_ai.processing import build_preprocessor, prepare_modeling_data


DEFAULT_DATA_PATH = Path("data/sample_data/credit_risk_sample.csv")
DEFAULT_ARTIFACTS_DIR = Path("ml/artifacts")
MODEL_VERSION = "credit-risk-mvp-v1"


@dataclass(frozen=True)
class TrainingRunSummary:
    model_version: str
    selected_model: str
    training_rows: int
    metrics_path: Path
    model_path: Path


def _candidate_models(random_state: int) -> dict[str, object]:
    # NOTE: class_weight="balanced" was tried and rejected. At this data's real
    # ~30% default rate, balanced weighting over-corrects: it trains the model as
    # if priors were 50/50, which shifts predicted probabilities well above true
    # frequencies (empirically: mean predicted P(default) ~0.42 vs the actual
    # ~0.30 base rate) without improving ROC-AUC. That miscalibration is what
    # made fixed risk-class thresholds (0.3/0.6) misfire — most applicants
    # scored "Medium" regardless of how safe their profile actually was. Natural
    # (unweighted) training keeps predict_proba anchored to real frequencies.
    return {
        "logistic_regression": LogisticRegression(max_iter=1000),
        "random_forest": RandomForestClassifier(
            n_estimators=250,
            max_depth=8,
            min_samples_leaf=6,
            random_state=random_state,
            n_jobs=1,
        ),
    }


def _load_data(data_path: Path | Sequence[Path]) -> pd.DataFrame:
    """Accepts a single CSV path, or multiple paths to concatenate (e.g. baseline +
    production, so retraining actually learns from newer labeled data instead of
    re-reading the same file it already knows)."""
    paths = [data_path] if isinstance(data_path, (str, Path)) else list(data_path)
    frames = [pd.read_csv(path) for path in paths]
    return pd.concat(frames, ignore_index=True) if len(frames) > 1 else frames[0]


def _compute_risk_thresholds(pipeline: Pipeline, features: pd.DataFrame) -> dict[str, float]:
    """Derive Low/Medium/High cutoffs from the winning model's OWN predicted
    probability distribution over the full available dataset, instead of
    arbitrary fixed numbers (0.3/0.6) that assume a probability distribution
    the model doesn't actually produce. Anchoring "Medium" at the median and
    "High" at the 85th percentile means risk tiers always reflect this model's
    real spread, and stay valid across retrains even if the score distribution
    shifts (e.g. after a champion/challenger promotion)."""
    probabilities = pipeline.predict_proba(features)[:, 1]
    return {
        "medium": round(float(np.quantile(probabilities, 0.50)), 4),
        "high": round(float(np.quantile(probabilities, 0.85)), 4),
    }


def _append_metrics_history(artifacts_dir: Path, entry: dict[str, object]) -> None:
    history_path = artifacts_dir / "metrics_history.json"
    history: list[dict[str, object]] = []
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    history.append(entry)
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")


def train_credit_risk_model(
    data_path: Path | Sequence[Path] = DEFAULT_DATA_PATH,
    artifacts_dir: Path = DEFAULT_ARTIFACTS_DIR,
    random_state: int = 42,
    record_history: bool = True,
) -> TrainingRunSummary:
    dataframe = _load_data(data_path)
    engineered = add_credit_risk_features(dataframe)
    features, target, schema = prepare_modeling_data(engineered)

    x_train, x_test, y_train, y_test = train_test_split(
        features,
        target,
        test_size=0.2,
        random_state=random_state,
        stratify=target,
    )

    results: dict[str, dict[str, object]] = {}
    trained_pipelines: dict[str, Pipeline] = {}
    for model_name, model in _candidate_models(random_state).items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", build_preprocessor(schema)),
                ("model", model),
            ]
        )
        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)
        probabilities = pipeline.predict_proba(x_test)[:, 1]
        results[model_name] = evaluate_classifier(y_test, predictions, probabilities)
        trained_pipelines[model_name] = pipeline

    selected_model = max(
        results,
        key=lambda name: (float(results[name]["roc_auc"]), float(results[name]["f1_score"])),
    )

    artifacts_dir.mkdir(parents=True, exist_ok=True)
    model_path = artifacts_dir / "model.pkl"
    preprocessor_path = artifacts_dir / "preprocessor.pkl"
    metrics_path = artifacts_dir / "metrics.json"

    joblib.dump(trained_pipelines[selected_model], model_path)
    joblib.dump(trained_pipelines[selected_model].named_steps["preprocessor"], preprocessor_path)

    risk_thresholds = _compute_risk_thresholds(trained_pipelines[selected_model], features)

    metrics_payload = {
        "model_version": MODEL_VERSION,
        "selected_model": selected_model,
        "selection_metric": "roc_auc_then_f1_score",
        "training_rows": int(len(x_train)),
        "test_rows": int(len(x_test)),
        "models": results,
        "risk_thresholds": risk_thresholds,
    }
    metrics_path.write_text(json.dumps(metrics_payload, indent=2), encoding="utf-8")

    if record_history:
        _append_metrics_history(
            artifacts_dir,
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "selected_model": selected_model,
                "training_rows": int(len(x_train)),
                "test_rows": int(len(x_test)),
                "roc_auc": results[selected_model]["roc_auc"],
                "f1_score": results[selected_model]["f1_score"],
                "accuracy": results[selected_model]["accuracy"],
            },
        )

    return TrainingRunSummary(
        model_version=MODEL_VERSION,
        selected_model=selected_model,
        training_rows=len(x_train),
        metrics_path=metrics_path,
        model_path=model_path,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Train LoanScore credit risk models.")
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--artifacts-dir", type=Path, default=DEFAULT_ARTIFACTS_DIR)
    args = parser.parse_args()

    summary = train_credit_risk_model(data_path=args.data, artifacts_dir=args.artifacts_dir)
    print(f"Selected {summary.selected_model}; saved model to {summary.model_path}")


if __name__ == "__main__":
    main()
