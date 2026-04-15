from typing import Sequence

from sqlalchemy import text
from sqlalchemy.engine.row import RowMapping
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session


def get_bad_singal_cells_records(db: Session) -> Sequence[RowMapping]:
    try:
        result = db.execute(text("""
            select
                center_lat,
                center_lon,
                min_lat,
                max_lat,
                min_lon,
                max_lon,
                total_events,
                rejected_events,
                avg_signal,
                rejection_ratio,
                is_bad_zone
            from mart_bad_signal_cells
        """))
        return result.mappings().all()
    except ProgrammingError as exc:
        # dbt owns the table, it has not been run yet
        if "mart_bad_signal_cells" in str(exc):
            return []
        return []