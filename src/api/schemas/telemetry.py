from datetime import datetime

from pydantic import BaseModel

from src.enums import TelemetryPipelineStage, TelemetryStatus

"""
    Request Schemass
"""

"""
    Public Schemas
"""
class TelemetryIngestRequest(BaseModel):
    dog_id: str
    event_ts: datetime
    latitude: float
    longitude: float
    cumulative_steps: int
    heart_rate: int
    battery: int
    signal_strength: int

class TelemetryIngestResponse(BaseModel):
    event_id: str
    status: TelemetryStatus
    pipeline_information: dict[TelemetryPipelineStage, bool]
    detail: str

"""
    Internal Schemas
"""

