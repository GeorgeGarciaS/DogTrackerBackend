from fastapi import APIRouter, status

from src.services.dog_service import get_dog, list_dogs, create_dog
from src.api.schemas.dog import DogCreateRequest, DogRequest, DogInternalResponse

router = APIRouter(prefix="/internal/dogs", tags=["dogs"])


@router.get(
    "",
    response_model=list[DogInternalResponse],
    summary="List dogs",
    description="Retrieve a list of all dogs in the system.",
)
def list_dogs_route() -> list[DogInternalResponse]:
    dogs = list_dogs()
    return [DogInternalResponse.model_validate(dog) for dog in dogs]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DogInternalResponse,
    summary="Create a dog",
    description="Create a new dog entry in the system.",
)
def create_dog_route(payload: DogCreateRequest) -> DogInternalResponse:
    dog = create_dog(payload)
    return DogInternalResponse.model_validate(dog)

@router.get(
    "/{dog_id}",
    response_model=DogInternalResponse,
    summary="Get dog",
    description="Retrieve a dog by ID.",
)
def get_dog_route(payload: DogRequest) -> DogInternalResponse:
    dog = get_dog(payload)
    return DogInternalResponse.model_validate(dog)


