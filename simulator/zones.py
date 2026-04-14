import random
from dataclasses import dataclass

from simulator.movement import BOUNDARY


@dataclass
class Zone:
    name: str
    min_lat: float
    max_lat: float
    min_lon: float
    max_lon: float
    min_signal: int
    max_signal: int

# get bad zone, one quarter of the space
MID_LAT = (BOUNDARY["min_lat"] + BOUNDARY["max_lat"]) / 2
BAD_ZONE = Zone(
    name="bad_zone",
    min_lat=MID_LAT,
    max_lat=BOUNDARY["max_lat"],
    min_lon=BOUNDARY["min_lon"],
    max_lon=BOUNDARY["max_lon"],
    min_signal=5,
    max_signal=40,
)

GOOD_ZONE = Zone(
    name="good_zone",
    min_lat=BOUNDARY["min_lat"],
    max_lat=BOUNDARY["max_lat"],
    min_lon=BOUNDARY["min_lon"],
    max_lon=BOUNDARY["max_lon"],
    min_signal=70,
    max_signal=100,
)

def get_signal_quality(
    latitude: float,
    longitude: float,
    prev_signal: int | None = None,
) -> int:
    if is_inside_zone(latitude, longitude, BAD_ZONE):
        min_signal = BAD_ZONE.min_signal
        max_signal = BAD_ZONE.max_signal
        step = 3   # small changes in bad zone
    else:
        min_signal = GOOD_ZONE.min_signal
        max_signal = GOOD_ZONE.max_signal
        step = 5   # slightly bigger changes in good zone
        prev_signal = None

    # First value
    if prev_signal is None:
        return random.randint(min_signal, max_signal)

    # Smooth transition
    delta = random.randint(-step, step)
    new_signal = prev_signal + delta

    # Clamp to zone bounds
    new_signal = max(min_signal, min(max_signal, new_signal))

    return new_signal

"""
    implementation helpers
"""

def is_inside_zone(latitude: float, longitude: float, zone: Zone) -> bool:
    return (
        zone.min_lat <= latitude <= zone.max_lat
        and zone.min_lon <= longitude <= zone.max_lon
    )


def is_inside_boundary(latitude: float, longitude: float) -> bool:
    return (
        BOUNDARY["min_lat"] <= latitude <= BOUNDARY["max_lat"]
        and BOUNDARY["min_lon"] <= longitude <= BOUNDARY["max_lon"]
    )