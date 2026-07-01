"""
Champion/challenger retraining.

"Retraining" only means something if the challenger is trained on data the
champion never saw (baseline + production combined, see model_training._load_data),
and only takes over if it's actually better — not a blind overwrite. This module
trains a challenger into a scratch directory, compares it against the currently
deployed champion on the SAME metric LoanScore already uses to pick between
model types (ROC-AUC, then F1 as a tiebreaker), and only promotes it (copies its
artifacts over the live model.pkl/preprocessor.pkl/metrics.json) if it wins.

Every attempt — promoted or not — is recorded in metrics_history.json so there's
a real audit trail of retraining runs over time.
"""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from modelvaultai_ai.model_training import DEFAULT_ARTIFACTS_DIR, train_credit_risk_model

DEFAULT_BASELINE_PATH = Path("data/sample_data/credit_risk_sample.csv")
DEFAULT_PRODUCTION_PATH = Path("data/sample_data/credit_risk_production.csv")


@dataclass(frozen=True)
class RetrainingRunResult:
    promoted: bool
    reason: str
    champion_metrics: dict[str, object] | None
    challenger_metrics: dict[str, object]
    challenger_model_name: str
    training_rows: int


def _read_metrics(metrics_path: Path) -> dict[str, object] | None:
    if not metrics_path.exists():
        return None
    payload = json.loads(metrics_path.read_text(encoding="utf-8"))
    selected = payload["selected_model"]
    return {**payload["models"][selected], "selected_model": selected}


def _is_better(challenger: dict[str, object], champion: dict[str, object] | None) -> bool:
    if champion is None:
        return True
    return (float(challenger["roc_auc"]), float(challenger["f1_score"])) > (
        float(champion["roc_auc"]),
        float(champion["f1_score"]),
    )


def run_retraining_challenge(
    baseline_path: Path = DEFAULT_BASELINE_PATH,
    production_path: Path = DEFAULT_PRODUCTION_PATH,
    artifacts_dir: Path = DEFAULT_ARTIFACTS_DIR,
) -> RetrainingRunResult:
    champion_metrics = _read_metrics(artifacts_dir / "metrics.json")

    challenger_dir = artifacts_dir / "challenger"
    summary = train_credit_risk_model(
        data_path=[baseline_path, production_path],
        artifacts_dir=challenger_dir,
        record_history=False,  # only the promotion decision gets one history entry, not two
    )
    challenger_metrics = _read_metrics(challenger_dir / "metrics.json")
    assert challenger_metrics is not None

    promote = _is_better(challenger_metrics, champion_metrics)

    if promote:
        for filename in ("model.pkl", "preprocessor.pkl", "metrics.json"):
            shutil.copy(challenger_dir / filename, artifacts_dir / filename)
        reason = (
            f"Challenger ({challenger_metrics['selected_model']}, "
            f"ROC-AUC {challenger_metrics['roc_auc']}) beat the champion "
            f"({champion_metrics['roc_auc'] if champion_metrics else 'none deployed yet'}) "
            f"trained on baseline + production data ({summary.training_rows} rows). Promoted."
        )
    else:
        reason = (
            f"Challenger ({challenger_metrics['selected_model']}, "
            f"ROC-AUC {challenger_metrics['roc_auc']}) did not beat the current champion "
            f"({champion_metrics['roc_auc']}). Champion kept in production."
        )

    history_path = artifacts_dir / "metrics_history.json"
    history: list[dict[str, object]] = []
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    history.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "selected_model": challenger_metrics["selected_model"],
            "training_rows": summary.training_rows,
            "test_rows": None,
            "roc_auc": challenger_metrics["roc_auc"],
            "f1_score": challenger_metrics["f1_score"],
            "accuracy": challenger_metrics["accuracy"],
            "event": "retraining_run",
            "promoted": promote,
        }
    )
    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")

    shutil.rmtree(challenger_dir, ignore_errors=True)

    return RetrainingRunResult(
        promoted=promote,
        reason=reason,
        champion_metrics=champion_metrics,
        challenger_metrics=challenger_metrics,
        challenger_model_name=challenger_metrics["selected_model"],
        training_rows=summary.training_rows,
    )
