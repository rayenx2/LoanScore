from fastapi import APIRouter

from app.schemas.reporting import MonitoringReportResponse
from app.services.reporting_service import generate_monitoring_report, get_latest_monitoring_report


router = APIRouter()


@router.get("/monitoring-report", response_model=MonitoringReportResponse)
def monitoring_report() -> MonitoringReportResponse:
    return get_latest_monitoring_report()


@router.post("/monitoring-report/generate", response_model=MonitoringReportResponse)
def monitoring_report_generate() -> MonitoringReportResponse:
    return generate_monitoring_report()
