import os
import time

from simulator.movement import update_dog_movement
from simulator.state import create_initial_dog_state
from simulator.zones import get_signal_quality

BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")

# wait for backend setup
time.sleep(5)

def main() -> None:
    dog = create_initial_dog_state()

    dog.dog_id = "111aaa"

    while True:
        dog = update_dog_movement(dog, tick_seconds=1.0)
        signal = get_signal_quality(dog.latitude, dog.longitude)

        print(
            f"lat={dog.latitude:.6f} "
            f"lon={dog.longitude:.6f} "
            f"heading={dog.heading_deg:.1f} "
            f"moving={dog.is_moving}"
        )

        time.sleep(1)


if __name__ == "__main__":
    main()