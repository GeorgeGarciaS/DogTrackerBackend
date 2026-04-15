import random
from copy import deepcopy
from datetime import datetime, timedelta


def apply_signal_effects(
    clean_payload: dict,
    signal_strength: int,
    previous_payload: dict | None,
) -> tuple[dict, str]:
    """
        Modes:
        - clean
        - degraded
        - stale
        - invalid
    """
    payload = deepcopy(clean_payload)

    # Good signal: send clean telemetry
    if signal_strength >= 50:
        return payload, "clean"

    roll = random.random()

    if roll < 0.40:
        return make_degraded_payload(payload), "degraded information"

    if roll < 0.60:
        return make_stale_payload(payload, previous_payload), "duplicated information"

    return make_bad_payload(payload), "corrupted information"


def make_degraded_payload(payload: dict) -> dict:
    """
        Valid but noisy:
        - slight GPS drift
        - lower signal strength
    """
    degraded = deepcopy(payload)

    degraded["latitude"] += random.uniform(-0.00005, 0.00005)
    degraded["longitude"] += random.uniform(-0.00005, 0.00005)

    degraded["signal_strength"] = max(
        0, min(100, degraded["signal_strength"] - random.randint(5, 20))
    )

    return degraded


def make_stale_payload(payload: dict, previous_payload: dict | None) -> dict:
    """
    Stale / duplicate:
    - if previous payload exists, resend it
    - otherwise send current payload with older timestamp
    """
    if previous_payload is not None:
        return deepcopy(previous_payload)

    stale = deepcopy(payload)
    dt = datetime.fromisoformat(stale["event_ts"])
    stale["event_ts"] = (dt - timedelta(seconds=15)).isoformat()

    return stale


def make_bad_payload(payload: dict) -> dict:
    """
    Break one field so backend validation / DQ catches it.
    """
    bad = deepcopy(payload)

    field_to_break = random.choice(
        [
            "latitude",
            "longitude",
            "battery",
            "heart_rate",
            "signal_strength",
            "cumulative_steps",
        ]
    )

    if field_to_break == "latitude":
        bad["latitude"] = 999.0
    elif field_to_break == "longitude":
        bad["longitude"] = 999.0
    elif field_to_break == "battery":
        bad["battery"] = 999
    elif field_to_break == "heart_rate":
        bad["heart_rate"] = -1
    elif field_to_break == "signal_strength":
        bad["signal_strength"] = 999
    elif field_to_break == "cumulative_steps":
        bad["cumulative_steps"] = -1

    return bad