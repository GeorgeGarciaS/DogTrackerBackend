from fastapi import APIRouter

from src.services.analytics_service import analytics_summary
from src.api.schemas.analytics import AnalyticsSummary


router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def analytics_summary_route() -> AnalyticsSummary:
    return analytics_summary()