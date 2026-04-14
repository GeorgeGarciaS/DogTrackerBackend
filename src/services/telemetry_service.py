from sqlalchemy.orm import Session

from src.helpers import normalize_ts
from src.api.exceptions import DomainError
from src.api.schemas.telemetry import (
    TelemetryIngestRequest,
    TelemetryIngestResponse,
)
from src.db.models.data_quality_issue import DataQualityIssueModel
from src.db.models.telemetry_clean import TelemetryCleanModel
from src.db.models.telemetry_raw import TelemetryRawModel
from src.db.repositories.data_quality_issue_repo import insert_data_quality_issue
from src.db.repositories.dog_current_status_repo import (
    get_dog_current_status_by_id,
    upsert_current_status,
)
from src.db.repositories.dog_repo import get_dog_by_id
from src.db.repositories.telemetry_repo import (
    insert_clean_telemetry,
    insert_raw_telemetry,
)
from src.enums import (
    DogErrorType,
    TelemetryIssueType,
    TelemetryPipelineStage,
    TelemetryStatus,
)
from src.validation.telemetry_checks import (
    validate_is_duplicate,
    validate_telemetry_ingest,
)


def ingest_telemetry(
    payload: TelemetryIngestRequest,
    db: Session
) -> TelemetryIngestResponse:
    pipeline = create_pipeline_information_obj()
    pipeline[TelemetryPipelineStage.API] = True

    dog = get_dog_by_id(payload.dog_id, db)
    if dog is None:
        pipeline[TelemetryPipelineStage.INVALID_TELEMETRY] = True
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

    duplicate_error = validate_is_duplicate(payload, db)
    errors = validate_telemetry_ingest(payload)
    if duplicate_error:
        errors.append(TelemetryIssueType.DUPLICATE_EVENT)
    
    insert_raw_telemetry(raw_telemetry_record, db)
    pipeline[TelemetryPipelineStage.TELEMETRY_RAW_INGEST] = True
    if not (errors == []):
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
        pipeline[TelemetryPipelineStage.DATA_QUALITY_ISSUES_INGEST] = True
        pipeline[TelemetryPipelineStage.TELEMETRY_REJECTED] = True
        return TelemetryIngestResponse(
            event_id=raw_telemetry_record.event_id,
            status=TelemetryStatus.REJECTED,
            pipeline_information=pipeline,
            detail=", ".join(errors),
        )

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
    pipeline[TelemetryPipelineStage.TELEMETRY_ACCEPTED] = True
    dog_current_status = get_dog_current_status_by_id(clean_telemetry_record.dog_id, db)
    if (
        dog_current_status is not None and
        normalize_ts(clean_telemetry_record.event_ts) >= normalize_ts(dog_current_status.last_event_ts)
    ) or dog_current_status is None: 
        upsert_current_status(clean_telemetry_record, db)
        pipeline[TelemetryPipelineStage.STATUS_UPDATED] = True
    db.commit()

    return TelemetryIngestResponse(
        event_id=raw_telemetry_record.event_id,
        status=TelemetryStatus.ACCEPTED,
        pipeline_information=pipeline,
        detail=""
    )

"""
    Implementation Helpers
"""

def create_pipeline_information_obj() -> dict[
    TelemetryPipelineStage,
    bool
]:
    pipeline = {}

    for stage in TelemetryPipelineStage:
        pipeline[stage] = False

    return pipeline