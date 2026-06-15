from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DBSession
from app.core.database import get_db
from app.core.auth import get_current_user
from app.models.schemas import AnalyticsResponse
from app.services import analytics_service

router = APIRouter()


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_analytics(
    db: DBSession = Depends(get_db),
    user: dict = Depends(get_current_user),
):
    stats = analytics_service.get_user_stats(db, user["user_id"])
    return AnalyticsResponse(**stats)
