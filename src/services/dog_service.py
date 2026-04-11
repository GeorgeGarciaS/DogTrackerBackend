import random
from src.api.schemas.dog import DogCreateRequest, Dog


def create_dog(payload: DogCreateRequest) -> Dog:
    return Dog(
        id=random.randint(1, 1000),
        name=payload.name,
        breed=payload.breed,
        age=payload.age,
    )