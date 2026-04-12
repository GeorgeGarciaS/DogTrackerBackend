from datetime import datetime

from pydantic import BaseModel

from src.enums import TelemetryIssueType

"""
    Request Schemass
"""
class DataQualityIssueRequest(BaseModel):
    event_id: str

"""
    Public Schemas
"""
class DataQualityIssueResponse(BaseModel):
    issue_id: str
    event_id: str
    dog_id: str
    issue_type: TelemetryIssueType
    issue_reason: str
    created_at: datetime

    model_config = {"from_attributes": True}
"""
    Internal Schemas
"""