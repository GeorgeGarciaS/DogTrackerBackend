from fastapi import APIRouter

from src.api.schemas.analytics import AnalyticsSummary
from src.services.analytics_service import get_analytics_summary

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/summary",
    response_model=AnalyticsSummary,
    summary="Dog analytics summary",
    description="Get aggregated analytics about dogs (e.g. count, averages).",
)
def analytics_summary_route() -> AnalyticsSummary:
    return get_analytics_summary()