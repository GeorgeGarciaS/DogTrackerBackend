from datetime import datetime

from sqlalchemy.orm import Session

from src.db.models.telemetry_clean import TelemetryCleanModel
from src.db.models.telemetry_raw import TelemetryRawModel


def insert_raw_telemetry(telemetry_record: TelemetryRawModel, db: Session):
    db.add(telemetry_record)
    db.flush()

def insert_clean_telemetry(telemetry_record: TelemetryCleanModel, db: Session):
    db.add(telemetry_record)


def get_duplicate_telemetry_event(
    dog_id: str,
    event_ts: datetime,
    latitude: float,
    longitude: float,
    cumulative_steps: int,
    heart_rate: int,
    battery: int,
    signal_strength: int,
    db: Session,
) -> TelemetryRawModel | None:
    return (
        db.query(TelemetryRawModel)
        .filter(
            TelemetryRawModel.dog_id == dog_id,
            TelemetryRawModel.event_ts == event_ts,
            TelemetryRawModel.latitude == latitude,
            TelemetryRawModel.longitude == longitude,
            TelemetryRawModel.cumulative_steps == cumulative_steps,
            TelemetryRawModel.heart_rate == heart_rate,
            TelemetryRawModel.battery == battery,
            TelemetryRawModel.signal_strength == signal_strength,
        )
        .first()
    )