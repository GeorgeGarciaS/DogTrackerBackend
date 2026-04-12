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

"""
    Internal Schemas
"""

