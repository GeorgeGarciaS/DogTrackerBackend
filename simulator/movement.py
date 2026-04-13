import math
import random
from datetime import datetime, timezone

from simulator.state import DogState

EARTH_METERS_PER_DEG_LAT = 111_320.0

# 200m x 200m rectangle based on dog starting coor
BOUNDARY = {
    "min_lat": 37.7740,
    "max_lat": 37.7760,
    "min_lon": -122.4205,
    "max_lon": -122.4180,
}

def normalize_heading(heading_deg: float) -> float:
    """
        Keep heading in the range [0, 360)
    """
    return heading_deg % 360.0


def meters_to_lat_lon_delta(
    distance_m: float,
    heading_deg: float,
    latitude_deg: float,
) -> tuple[float, float]:
    """
        Convert a movement step in meters into latitude/longitude changes
    """
    heading_rad = math.radians(heading_deg)

    north_m = math.cos(heading_rad) * distance_m
    east_m = math.sin(heading_rad) * distance_m

    delta_lat = north_m / EARTH_METERS_PER_DEG_LAT

    meters_per_deg_lon = EARTH_METERS_PER_DEG_LAT * math.cos(math.radians(latitude_deg))
    if abs(meters_per_deg_lon) < 1e-6:
        delta_lon = 0.0
    else:
        delta_lon = east_m / meters_per_deg_lon

    return delta_lat, delta_lon


def update_dog_movement(
    dog: DogState,
    tick_seconds: float = 1.0,
    max_turn_deg: float = 18.0,
    pause_probability: float = 0.08,
    speed_jitter: float = 0.15,
) -> DogState:
    """
        Update dog position with random movement
        - heading adjustments
        - pauses
        - speed variation
    """
    new_heading = normalize_heading(
        dog.heading_deg + random.uniform(-max_turn_deg, max_turn_deg)
    )

    is_moving = random.random() > pause_probability

    actual_speed = dog.speed_mps
    if is_moving:
        speed_multiplier = random.uniform(1.0 - speed_jitter, 1.0 + speed_jitter)
        actual_speed = max(0.0, dog.speed_mps * speed_multiplier)
        distance_m = actual_speed * tick_seconds
    else:
        distance_m = 0.0

    delta_lat, delta_lon = meters_to_lat_lon_delta(
        distance_m=distance_m,
        heading_deg=new_heading,
        latitude_deg=dog.latitude,
    )

    dog.heading_deg = new_heading
    dog.latitude += delta_lat
    dog.longitude += delta_lon
    dog.is_moving = is_moving
    dog.last_update_ts = datetime.now(timezone.utc)

    apply_boundary_behavior(dog, BOUNDARY)
    return dog

def apply_boundary_behavior(dog: DogState, boundary: dict) -> None:
    # turn in small increments before edge
    buffer = 0.0001

    near_north = dog.latitude > boundary["max_lat"] - buffer
    near_south = dog.latitude < boundary["min_lat"] + buffer
    near_east = dog.longitude > boundary["max_lon"] - buffer
    near_west = dog.longitude < boundary["min_lon"] + buffer

    if near_north:
        dog.heading_deg = random.uniform(180, 360)

    elif near_south:
        dog.heading_deg = random.uniform(0, 180)

    if near_east:
        dog.heading_deg = random.uniform(180, 360)

    elif near_west:
        dog.heading_deg = random.uniform(0, 180)  