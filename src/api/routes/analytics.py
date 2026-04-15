
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.api.schemas.analytics import AnalyticsSummary, SignalsZoneBoundsResponse
from src.db.session import get_db
from src.services.analytics_service import get_analytics_summary, get_bad_signal_cells

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get(
    "/summary",
    response_model=AnalyticsSummary,
    summary="Dog analytics summary",
    description="Get aggregated analytics about dogs (e.g. count, averages).",
)
def analytics_summary_route() -> AnalyticsSummary:
    return get_analytics_summary()

@router.get(
    "/signal-zone-bounds",
    response_model=list[SignalsZoneBoundsResponse],
    summary="Figure out bad signal locations",
    description="get the grid output of the bad signal spots in a map by lat lon.",
)
def get_bad_signal_cells_route(
    db: Session = Depends(get_db)
) -> list[SignalsZoneBoundsResponse]:
    bad_signal_cells = get_bad_signal_cells(db)
    
    return [SignalsZoneBoundsResponse.model_validate(cell) for cell in bad_signal_cells]