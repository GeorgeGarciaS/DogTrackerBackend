from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class TelemetryModelFieldsMixin:
    dog_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("dogs.dog_id"),
        nullable=False,
        comment="Foreign key referencing dogs.dog_id"
    )

    event_ts: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Timestamp reported by the device or simulator"
    )

    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Raw latitude value from device"
    )

    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Raw longitude value from device"
    )

    cumulative_steps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Cumulative step count since last reset"
    )

    heart_rate: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Heart rate in beats per minute (BPM)"
    )

    battery: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Battery level percentage (0-100 expected)"
    )

    signal_strength: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Normalized signal strength value (0-100 expected)"
    )

    ingested_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
        comment="Timestamp when the event was ingested by backend"
    )
