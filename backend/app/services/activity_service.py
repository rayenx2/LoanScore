"""In-memory tracking of prediction, drift-check and reporting activity.

This gives the dashboard a lightweight "what has this model been doing"
view without requiring an external database. State resets on restart,
which is acceptable for a portfolio / demo deployment.
"""

from collections import deque
from datetime import datetime, timezone
from threading import Lock

from app.schemas.activity import ActivityEvent, ActivityResponse, ActivitySummary


_MAX_EVENTS = 200
_events: deque[ActivityEvent] = deque(maxlen=_MAX_EVENTS)
_lock = Lock()

_total_predictions = 0
_total_drift_checks = 0
_total_reports_generated = 0
_high_risk_predictions = 0
_probability_sum = 0.0
_last_drift_detected: bool | None = None
_last_model_health_score: int | None = None


def _now() -> datetime:
    return datetime.now(timezone.utc)


def record_prediction(applicant_id: str, risk_class: str, default_probability: float) -> None:
    global _total_predictions, _high_risk_predictions, _probability_sum

    with _lock:
        _total_predictions += 1
        _probability_sum += default_probability
        if risk_class.lower() == "high":
            _high_risk_predictions += 1

        _events.append(
            ActivityEvent(
                timestamp=_now(),
                event_type="prediction",
                applicant_id=applicant_id,
                risk_class=risk_class,
                default_probability=default_probability,
            )
        )


def record_drift_check(drift_detected: bool) -> None:
    global _total_drift_checks, _last_drift_detected

    with _lock:
        _total_drift_checks += 1
        _last_drift_detected = drift_detected

        _events.append(
            ActivityEvent(
                timestamp=_now(),
                event_type="drift_check",
                drift_detected=drift_detected,
            )
        )


def record_model_health(score: int) -> None:
    global _last_model_health_score

    with _lock:
        _last_model_health_score = score

        _events.append(
            ActivityEvent(
                timestamp=_now(),
                event_type="model_health",
                model_health_score=score,
            )
        )


def record_report_generated() -> None:
    global _total_reports_generated

    with _lock:
        _total_reports_generated += 1

        _events.append(
            ActivityEvent(
                timestamp=_now(),
                event_type="monitoring_report",
            )
        )


def record_retraining_run(promoted: bool) -> None:
    with _lock:
        _events.append(
            ActivityEvent(
                timestamp=_now(),
                event_type="retraining_run",
                promoted=promoted,
            )
        )


def get_activity(limit: int = 20) -> ActivityResponse:
    with _lock:
        average_probability = (
            _probability_sum / _total_predictions if _total_predictions else None
        )

        summary = ActivitySummary(
            total_predictions=_total_predictions,
            total_drift_checks=_total_drift_checks,
            total_reports_generated=_total_reports_generated,
            high_risk_predictions=_high_risk_predictions,
            average_default_probability=average_probability,
            last_drift_detected=_last_drift_detected,
            last_model_health_score=_last_model_health_score,
        )

        recent_events = list(_events)[-limit:][::-1]

    return ActivityResponse(summary=summary, recent_events=recent_events)
