import random

from simulator.state import DogState


def update_heart_rate(dog: DogState):
    """
    Simple heart rate model.
    """
    base = 95 if dog.is_moving else 70

    # move towards target
    dog.heart_rate = dog.heart_rate + int((base - dog.heart_rate) * 0.3)

    # small randomness
    dog.heart_rate += random.randint(-2, 2)
    dog.heart_rate = max(50, min(140, dog.heart_rate))



def update_cumulative_steps(dog: DogState, comulative_steps_counter: int):
    """
    Increment steps only if moving.
    """
    if not dog.is_moving:
        return dog.cumulative_steps

    # increase steps not every tick
    if comulative_steps_counter % 2 == 0:
        dog.cumulative_steps += 1
