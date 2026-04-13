import os
import time

from simulator.collar_client import build_telemetry_payload, create_dog, send_telemetry
from simulator.movement import update_dog_movement
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

    while True:
        dog = update_dog_movement(dog, tick_seconds=1.0)
        signal = get_signal_quality(dog.latitude, dog.longitude)
        write_sim_state(dog, signal)
        payload = build_telemetry_payload(dog, signal)
        try:
            send_telemetry(payload, BASE_URL)
        except Exception as e:
            print(f"failed to send telemetry: {e}")

        print(
            f"lat={dog.latitude:.6f} "
            f"lon={dog.longitude:.6f} "
            f"heading={dog.heading_deg:.1f} "
            f"moving={dog.is_moving}"
        )

        time.sleep(1)


if __name__ == "__main__":
    main()