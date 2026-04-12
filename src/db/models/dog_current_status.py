from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.session import Base


class DogCurrentStatusModel(Base):
    __tablename__ = "dog_current_status"

    dog_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("dogs.dog_id"),
        primary_key=True,
        comment="Primary key and foreign key referencing dogs.dog_id (one row per dog)"
    )

    last_event_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        comment="Identifier of the latest accepted telemetry event"
    )

    last_event_ts: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        comment="Timestamp of the latest valid telemetry event"
    )

    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Latest valid latitude"
    )

    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="Latest valid longitude"
    )

    cumulative_steps: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Latest valid cumulative step count"
    )

    heart_rate: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Latest valid heart rate in BPM"
    )

    battery: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Latest valid battery level percentage (0-100 expected)"
    )

    signal_strength: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Latest valid signal strength (0-100 expected)"
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now(timezone.utc),
        comment="Timestamp when the current status was last updated by backend"
    )