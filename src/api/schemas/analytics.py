from pydantic import BaseModel

"""
    Request Schemass
"""

"""
    Public Schemas
"""
class AnalyticsSummary(BaseModel):
    total_dogs: int
    active_devices: int
    avg_daily_distance_km: int


class SignalsZoneBoundsResponse(BaseModel):
    center_lat: float
    center_lon: float
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    total_events: int
    rejected_events: int
    avg_signal: float
    rejection_ratio: float
    is_bad_zone: bool

    model_config = {"from_attributes": True}

"""
    Internal Schemas
"""

