from fastapi import APIRouter, status

from src.api.schemas.dog import DogResponse, DogCreateRequest, DogRequest
from src.services.dog_service import create_dog, list_dogs, get_dog


router = APIRouter(prefix="/dogs", tags=["dogs"])


@router.get(
    "",
    response_model=list[DogResponse],
    summary="List dogs",
    description="Retrieve a list of all dogs in the system.",
)
def list_dogs_route() -> list[DogResponse]:
    dogs = list_dogs()
    return [DogResponse.model_validate(dog) for dog in dogs]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DogResponse,
    summary="Create a dog",
    description="Create a new dog entry in the system.",
)
def create_dog_route(payload: DogCreateRequest) -> DogResponse:
    dog = create_dog(payload)
    return DogResponse.model_validate(dog)

@router.get(
    "/{dog_id}",
    response_model=DogResponse,
    summary="Get dog",
    description="Retrieve a dog by ID.",
)
def get_dog_route(payload: DogRequest) -> DogResponse:
    dog = get_dog(payload)
    return DogResponse.model_validate(dog)
