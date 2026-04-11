from pydantic import BaseModel


class AnalyticsSummary(BaseModel):
    total_dogs: int
    active_devices: int
    avg_daily_distance_km: int
