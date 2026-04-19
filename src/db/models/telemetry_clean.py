from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
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

    is_valid: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default="true",
        comment="Whether this clean telemetry record is still considered valid after downstream validation"
    )

    invalid_reason: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Reason the record was invalidated by downstream validation"
    )

    invalidated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Timestamp when the record was invalidated by downstream validation"
    )