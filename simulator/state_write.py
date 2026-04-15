import json
import os
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent / "runtime" / "sim_state.json"
SIM_STATE_PATH = Path(os.getenv("SIM_STATE_PATH", DEFAULT_PATH))
SIM_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)


def _load_existing_state() -> dict:
    if not SIM_STATE_PATH.exists():
        return {}
    try:
        return json.loads(SIM_STATE_PATH.read_text())
    except Exception:
        return {}


def write_sim_state(
    dog,
    signal_strength: int,
    telemetry_response: dict | None,
    last_event: str | None = None
) -> None:
    now_iso = datetime.now(timezone.utc).isoformat()
    existing = _load_existing_state()

    prev_event_seq = int(existing.get("event_seq", 0) or 0)
    prev_last_event = existing.get("last_event")
    prev_last_event_ts = existing.get("last_event_ts")
    prev_telemetry_pipeline_info = existing.get("telemetry_pipeline_info")

    next_last_event = prev_last_event
    next_last_event_ts = prev_last_event_ts
    next_event_seq = prev_event_seq
    next_telemetry_pipeline_info = prev_telemetry_pipeline_info

    if last_event is not None:
        assert telemetry_response is not None
        next_last_event = last_event
        next_last_event_ts = now_iso
        next_event_seq = prev_event_seq + 1
        next_telemetry_pipeline_info = telemetry_response.get("pipeline_information")

    payload = {
        "dog_id": dog.dog_id,
        "latitude": dog.latitude,
        "longitude": dog.longitude,
        "heading_deg": dog.heading_deg,
        "is_moving": dog.is_moving,
        "event_ts": dog.last_update_ts.isoformat(),
        "cumulative_steps": dog.cumulative_steps,
        "heart_rate": dog.heart_rate,
        "battery": dog.battery,
        "signal_strength": signal_strength,
        "last_event": next_last_event,
        "last_event_ts": next_last_event_ts,
        "event_seq": next_event_seq,
        "telemetry_pipeline_info": next_telemetry_pipeline_info,
    }

    SIM_STATE_PATH.write_text(json.dumps(payload, indent=2))