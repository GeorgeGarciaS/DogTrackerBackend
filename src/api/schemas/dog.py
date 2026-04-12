from datetime import datetime
from pydantic import BaseModel

"""
    Request Schemass
"""
class DogCreateRequest(BaseModel):
    name: str

class DogRequest(BaseModel):
    id: int

"""
    Public Schemas
"""
class DogResponse(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}

"""
    Internal Schemas
"""
class DogInternalResponse(BaseModel):
    dog_id: str
    name: str
    device_id: str
    start_lat: float
    start_lon: float
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}