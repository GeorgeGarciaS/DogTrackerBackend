from sqlalchemy.orm import Session

from src.api.schemas.telemetry import TelemetryIngestRequest
from src.db.repositories.telemetry_repo import get_duplicate_telemetry_event
from src.enums import TelemetryIssueType
from src.validation.helpers import validate_latitude, validate_longitude


def validate_telemetry_ingest(payload: TelemetryIngestRequest) -> list[str]:
    errors: list[str] = []

    if not (validate_latitude(payload.latitude)):
        errors.append(TelemetryIssueType.LATITUDE_OUT_OF_RANGE.value)

    if not (validate_longitude(payload.longitude)):
        errors.append(TelemetryIssueType.LONGITUDE_OUT_OF_RANGE.value)

    if not (0 <= payload.battery <= 100):
        errors.append(TelemetryIssueType.BATTERY_OUT_OF_RANGE.value)
    if payload.heart_rate <= 0:
        errors.append(TelemetryIssueType.HEART_RATE_INVALID.value)
    if not (0 <= payload.signal_strength <= 100):
        errors.append(TelemetryIssueType.SIGNAL_STRENGTH.value)
    
    if payload.cumulative_steps < 0:
        errors.append(TelemetryIssueType.CUMULATIVE_STEPS_OUT_OF_RANGE.value)
    return errors

def validate_is_duplicate(
    payload: TelemetryIngestRequest,
    db: Session,
) -> bool:
    existing_event = get_duplicate_telemetry_event(
        payload.dog_id,
        payload.event_ts,
        payload.latitude,
        payload.longitude,
        payload.cumulative_steps,
        payload.heart_rate,
        payload.battery,
        payload.signal_strength,
        db,
    )

    return existing_event is not None