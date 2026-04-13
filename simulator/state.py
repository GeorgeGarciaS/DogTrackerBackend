from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class DogState:
    dog_id: str
    latitude: float
    longitude: float
    heading_deg: float
    speed_mps: float
    is_moving: bool
    last_update_ts: datetime
    cumulative_steps: int
    heart_rate: int
    battery: int


def create_initial_dog_state() -> DogState:
    return DogState(
        dog_id="",
        latitude=37.7749,
        longitude=-122.4194,
        heading_deg=90.0,
        speed_mps=0.8,
        is_moving=True,
        last_update_ts=datetime.now(timezone.utc),
        cumulative_steps=0,
        heart_rate=88,
        battery=95,
    )