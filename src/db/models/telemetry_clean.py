from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.models.telemetry_mixin import TelemetryModelFieldsMixin
from src.db.session import Base


class TelemetryCleanModel(TelemetryModelFieldsMixin, Base):
    __tablename__ = "telemetry_clean"

    event_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("telemetry_raw.event_id"),
        primary_key=True,
        comment="Primary key UUID and foreign key to telemetry_raw event_id"
    )