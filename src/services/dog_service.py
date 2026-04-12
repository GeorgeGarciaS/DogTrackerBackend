import random
from datetime import datetime

from src.api.schemas.dog import DogCreateRequest, DogRequest
from src.db.models.dog import DogModel

def list_dogs() -> list[DogModel]:
    return [
        DogModel(
            dog_id="aaaa1111",
            name="Milo",
            device_id="aaaa1111",
            start_lat=random.uniform(-90, 90),
            start_lon=random.uniform(-180, 180),
            is_active=True,
            created_at=datetime.now(),
        ),
        DogModel(
            dog_id="aaaa1111",
            name="Milo",
            device_id="aaaa1111",
            start_lat=random.uniform(-90, 90),
            start_lon=random.uniform(-180, 180),
            is_active=True,
            created_at=datetime.now(),
        ),
    ]

def create_dog(payload: DogCreateRequest) -> DogModel:
    return DogModel(
        dog_id="aaaa1111",
        name="Milo",
        device_id="aaaa1111",
        start_lat=random.uniform(-90, 90),
        start_lon=random.uniform(-180, 180),
        is_active=True,
        created_at=datetime.now(),
    )

def get_dog(payload: DogRequest) -> DogModel:
    return DogModel(
        dog_id="aaaa1111",
        name="Milo",
        device_id="aaaa1111",
        start_lat=random.uniform(-90, 90),
        start_lon=random.uniform(-180, 180),
        is_active=True,
        created_at=datetime.now(),
    )