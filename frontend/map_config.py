from simulator.movement import BOUNDARY

MID_LAT = (BOUNDARY["min_lat"] + BOUNDARY["max_lat"]) / 2

BAD_ZONE = {
    "min_lat": MID_LAT,
    "max_lat": BOUNDARY["max_lat"],
    "min_lon": BOUNDARY["min_lon"],
    "max_lon": BOUNDARY["max_lon"],
}