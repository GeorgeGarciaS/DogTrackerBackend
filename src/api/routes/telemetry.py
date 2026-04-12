from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.api.exceptions import DomainError
from src.api.schemas.telemetry import TelemetryIngestRequest, TelemetryIngestResponse
from src.db.session import get_db
from src.services.telemetry_service import ingest_telemetry

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post(
    "",
    response_model=TelemetryIngestResponse,
    summary="Ingest telemetry",
    description="Ingest and save telemetry data from device.",
)
def ingest_telemetry_route(
    payload: TelemetryIngestRequest,
    db: Session = Depends(get_db)
) -> TelemetryIngestResponse:
    try:
        return ingest_telemetry(payload, db)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=e.issue.value)

