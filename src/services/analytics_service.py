import random
from src.api.schemas.analytics import AnalyticsSummary

def get_analytics_summary() -> AnalyticsSummary:
    return AnalyticsSummary(
        total_dogs=random.randint(1, 1000),
        active_devices=random.randint(1, 1000),
        avg_daily_distance_km=random.randint(1, 1000),
    )