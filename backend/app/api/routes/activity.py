from fastapi import APIRouter, Query

from app.schemas.activity import ActivityResponse
from app.services.activity_service import get_activity


router = APIRouter()


@router.get("/activity", response_model=ActivityResponse)
def activity(limit: int = Query(default=20, ge=1, le=200)) -> ActivityResponse:
    return get_activity(limit=limit)
