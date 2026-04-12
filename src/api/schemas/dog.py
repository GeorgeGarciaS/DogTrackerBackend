from datetime import datetime

from pydantic import BaseModel, Field, field_validator

"""
    Request Schemass
"""
class DogCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    start_latitude: float
    start_longitude: float
    
    @field_validator("name")
    @classmethod
    def clean_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("name must not be empty")
        return value

class DogRequest(BaseModel):
    dog_id: str

class DogCurrentStatusRequest(BaseModel):
    dog_id: str

"""
    Public Schemas
"""
class DogResponse(BaseModel):
    dog_id: str

    model_config = {"from_attributes": True}

class DogCurrentStatusResponse(BaseModel):
    dog_id: str
    last_event_id: str
    last_event_ts: datetime
    latitude: float
    longitude: float
    cumulative_steps: int
    heart_rate: int
    battery: int
    signal_strength: int
    updated_at: datetime

    model_config = {"from_attributes": True}

"""
    Internal Schemas
"""
class DogInternalResponse(BaseModel):
    dog_id: str
    name: str
    device_id: str
    start_latitude: float
    start_longitude: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}