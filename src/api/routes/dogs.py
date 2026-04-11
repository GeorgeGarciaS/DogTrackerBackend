from fastapi import APIRouter, status

from src.api.schemas.dog import DogsResponse, Dog, DogCreateRequest
from src.services.dog_service import create_dog


router = APIRouter(prefix="/dogs", tags=["dogs"])


@router.get("")
def list_dogs_route() -> DogsResponse:
    return DogsResponse(
        dogs=[
            Dog(id=1, name="Milo", breed="Beagle", age=4),
            Dog(id=2, name="Luna", breed="Border Collie", age=2),
        ]
    )


@router.post("", status_code=status.HTTP_201_CREATED)
def create_dog_route(payload: DogCreateRequest) -> Dog:
    return create_dog(payload)