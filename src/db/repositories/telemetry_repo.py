from sqlalchemy.orm import Session

from src.db.models.data_quality_issue import DataQualityIssueModel
from src.db.models.dog_current_status import DogCurrentStatusModel
from src.db.models.telemetry_clean import TelemetryCleanModel
from src.db.models.telemetry_raw import TelemetryRawModel


def insert_raw_telemetry(telemetry_record: TelemetryRawModel, db: Session):
    db.add(telemetry_record)
    db.flush()

def insert_clean_telemetry(telemetry_record: TelemetryCleanModel, db: Session):
    db.add(telemetry_record)

def insert_data_quality_issue(issue: DataQualityIssueModel, db: Session):
    db.add(issue)

def upsert_current_status(clean_telemetry_record: TelemetryCleanModel, db: Session):
    # find if there is a DogCurrentStatus with the dog_id of clean_telemetry_record
    status = db.query(DogCurrentStatusModel).filter(
        DogCurrentStatusModel.dog_id == clean_telemetry_record.dog_id
    ).first()

    if status is None:
        # instert
        status = DogCurrentStatusModel(
            dog_id=clean_telemetry_record.dog_id,
            last_event_id=clean_telemetry_record.event_id,
            last_event_ts=clean_telemetry_record.event_ts,
            latitude=clean_telemetry_record.latitude,
            longitude=clean_telemetry_record.longitude,
            cumulative_steps=clean_telemetry_record.cumulative_steps,
            heart_rate=clean_telemetry_record.heart_rate,
            battery=clean_telemetry_record.battery,
            signal_strength=clean_telemetry_record.signal_strength,
        )
        db.add(status)
    else:
        # update
        status.last_event_id = clean_telemetry_record.event_id
        status.last_event_ts = clean_telemetry_record.event_ts
        status.latitude = clean_telemetry_record.latitude
        status.longitude = clean_telemetry_record.longitude
        status.cumulative_steps = clean_telemetry_record.cumulative_steps
        status.heart_rate = clean_telemetry_record.heart_rate
        status.battery = clean_telemetry_record.battery
        status.signal_strength = clean_telemetry_record.signal_strength