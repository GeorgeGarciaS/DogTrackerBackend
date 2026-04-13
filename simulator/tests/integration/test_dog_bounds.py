from datetime import datetime, timezone

from simulator.movement import update_dog_movement
from simulator.state import DogState
from simulator.zones import BOUNDARY


def make_test_dog() -> DogState:
    return DogState(
        dog_id="test-dog",
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


def is_inside_boundary(latitude: float, longitude: float) -> bool:
    return (
        BOUNDARY["min_lat"] <= latitude <= BOUNDARY["max_lat"]
        and BOUNDARY["min_lon"] <= longitude <= BOUNDARY["max_lon"]
    )


def test_dog_stays_within_boundary_over_long_simulation():
    dog = make_test_dog()

    ticks = 5000

    for _ in range(0, ticks):
        dog = update_dog_movement(
            dog,
            tick_seconds=1.0,
            max_turn_deg=18.0,
            pause_probability=0.08,
            speed_jitter=0.15,
        )

        assert is_inside_boundary(
            dog.latitude,
            dog.longitude,
        ), (
            f"Dog went out of bounds at "
            f"lat={dog.latitude}, lon={dog.longitude}"
        )