from sqlalchemy.orm import Session

from src.api.exceptions import DomainError
from src.api.schemas.telemetry import TelemetryIngestRequest, TelemetryIngestResponse
from src.db.models.data_quality_issue import DataQualityIssueModel
from src.db.models.telemetry_clean import TelemetryCleanModel
from src.db.models.telemetry_raw import TelemetryRawModel
from src.db.repositories.dog_current_status_repo import upsert_current_status
from src.db.repositories.dog_repo import get_dog_by_id
from src.db.repositories.telemetry_repo import (
    insert_clean_telemetry,
    insert_data_quality_issue,
    insert_raw_telemetry,
)
from src.enums import DogErrorType, TelemetryStatus
from src.validation.telemetry_checks import validate_telemetry_ingest


def ingest_telemetry(
    payload: TelemetryIngestRequest,
    db: Session
) -> TelemetryIngestResponse:
    dog = get_dog_by_id(payload.dog_id, db)
    if dog is None:
        raise DomainError(DogErrorType.DOG_NOT_FOUND)
    
    # build and record raw record
    raw_telemetry_record = TelemetryRawModel(
        dog_id=payload.dog_id,
        event_ts=payload.event_ts,
        latitude=payload.latitude,
        longitude=payload.longitude,
        cumulative_steps=payload.cumulative_steps,
        heart_rate=payload.heart_rate,
        battery=payload.battery,
        signal_strength=payload.signal_strength,
    )

    insert_raw_telemetry(raw_telemetry_record, db)
    errors = validate_telemetry_ingest(payload)
    print("$$err", errors)
    if not (errors == []):
        print("$$in")
        for error in errors:
            insert_data_quality_issue(
                DataQualityIssueModel(
                    event_id=raw_telemetry_record.event_id,
                    dog_id=raw_telemetry_record.dog_id,
                    issue_type=error,
                    issue_reason=f"Validation failed: {error.replace('_', ' ')}",
                ),
                db
            )
        db.commit()
        return TelemetryIngestResponse(
            event_id=raw_telemetry_record.event_id,
            status=TelemetryStatus.REJECTED,
            detail=", ".join(errors),
        )
    print("$$in2")
    
    clean_telemetry_record = TelemetryCleanModel(
        event_id=raw_telemetry_record.event_id,
        dog_id=raw_telemetry_record.dog_id,
        event_ts=raw_telemetry_record.event_ts,
        latitude=raw_telemetry_record.latitude,
        longitude=raw_telemetry_record.longitude,
        cumulative_steps=raw_telemetry_record.cumulative_steps,
        heart_rate=raw_telemetry_record.heart_rate,
        battery=raw_telemetry_record.battery,
        signal_strength=raw_telemetry_record.signal_strength,
    )

    insert_clean_telemetry(clean_telemetry_record, db)
    upsert_current_status(clean_telemetry_record, db)
    db.commit()
    return TelemetryIngestResponse(
        event_id=raw_telemetry_record.event_id,
        status=TelemetryStatus.ACCEPTED,
        detail=""
    )