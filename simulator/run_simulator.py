import os
import time

from simulator.collar_client import build_telemetry_payload, create_dog, send_telemetry
from simulator.corruption import apply_signal_effects
from simulator.movement import update_dog_movement
from simulator.physiology import update_cumulative_steps, update_heart_rate
from simulator.state import create_initial_dog_state
from simulator.state_write import write_sim_state
from simulator.zones import get_signal_quality

BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

# wait for backend setup
time.sleep(5)

def main() -> None:
    dog = create_initial_dog_state()

    dog_id = create_dog(
        base_url=BASE_URL,
        name="Mr Fluffy",
        start_latitude=dog.latitude,
        start_longitude=dog.longitude,
    )
    dog.dog_id = dog_id

    telemetry_simulation_step_counter = 0
    comulative_steps_counter = 0

    previous_sent_payload: dict | None = None
    prev_signal: int | None = None
    while True:
        dog = update_dog_movement(dog, tick_seconds=1.0)
        signal = get_signal_quality(dog.latitude, dog.longitude, prev_signal)
        prev_signal = signal
        update_heart_rate(dog)
        update_cumulative_steps(dog, comulative_steps_counter)

        telemetry_simulation_step_counter += 1
        comulative_steps_counter +=1
        event_type = None
        mode = None
        telemetry_response = None
        # Only send every x steps for realism
        if telemetry_simulation_step_counter % 10 == 0:
            clean_payload = build_telemetry_payload(dog, signal)
            final_payload, mode = apply_signal_effects(
                clean_payload=clean_payload,
                signal_strength=signal,
                previous_payload=previous_sent_payload,
            )
            try:
                telemetry_response = send_telemetry(final_payload, BASE_URL)
                event_type = mode
                previous_sent_payload = final_payload
            except Exception as e:
                print(f"failed to send telemetry: {e}")
            print("SENT TELEMETRY")

        write_sim_state(dog, signal, telemetry_response, event_type)
        print(
            f"lat={dog.latitude:.6f} "
            f"lon={dog.longitude:.6f} "
            f"heading={dog.heading_deg:.1f} "
            f"moving={dog.is_moving}"
            f"signal={signal} "
            f"mode={mode}"
        )

        time.sleep(0.3)

if __name__ == "__main__":
    main()