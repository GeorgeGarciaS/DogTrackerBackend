import json
import os
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent / "runtime" / "sim_state.json"
SIM_STATE_PATH = Path(os.getenv("SIM_STATE_PATH", DEFAULT_PATH))

def write_sim_state(dog, signal_strength: int) -> None:
    SIM_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "dog_id": dog.dog_id,
        "latitude": dog.latitude,
        "longitude": dog.longitude,
        "heading_deg": dog.heading_deg,
        "speed_mps": dog.speed_mps,
        "is_moving": dog.is_moving,
        "event_ts": dog.last_update_ts.isoformat(),
        "cumulative_steps": dog.cumulative_steps,
        "heart_rate": dog.heart_rate,
        "battery": dog.battery,
        "signal_strength": signal_strength,
    }

    SIM_STATE_PATH.write_text(json.dumps(payload, indent=2))