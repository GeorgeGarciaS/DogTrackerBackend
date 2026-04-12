from src.api.schemas.telemetry import TelemetryIngestRequest
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

    if payload.cumulative_steps < 0:
        errors.append(TelemetryIssueType.CUMULATIVE_STEPS_OUT_OF_RANGE.value)
    return errors