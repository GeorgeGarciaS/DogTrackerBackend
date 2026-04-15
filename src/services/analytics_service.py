import random
from typing import Sequence

from sqlalchemy.engine.row import RowMapping
from sqlalchemy.orm import Session

from src.api.schemas.analytics import (
    AnalyticsSummary,
)
from src.db.repositories.analytics_repo import get_bad_singal_cells_records


def get_analytics_summary() -> AnalyticsSummary:
    return AnalyticsSummary(
        total_dogs=random.randint(1, 1000),
        active_devices=random.randint(1, 1000),
        avg_daily_distance_km=random.randint(1, 1000),
    )

def get_bad_signal_cells(db: Session) -> Sequence[RowMapping]:
    return get_bad_singal_cells_records(db)