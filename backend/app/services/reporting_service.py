from fastapi import HTTPException, status

from app.schemas.reporting import MonitoringReportResponse
from app.services.activity_service import record_report_generated
from modelvaultai_ai.reporting import generate_and_save_monitoring_report, load_latest_monitoring_report


def get_latest_monitoring_report() -> MonitoringReportResponse:
    try:
        return MonitoringReportResponse(**load_latest_monitoring_report())
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No monitoring report has been generated yet: {exc}",
        ) from exc


def generate_monitoring_report() -> MonitoringReportResponse:
    report = MonitoringReportResponse(**generate_and_save_monitoring_report())
    record_report_generated()
    return report
