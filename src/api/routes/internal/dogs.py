from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.api.exceptions import DomainError
from src.api.schemas.dog import DogCreateRequest, DogInternalResponse, DogRequest
from src.db.session import get_db
from src.services.dog_service import create_dog, get_dog, list_dogs

router = APIRouter(prefix="/internal/dogs", tags=["dogs"])


@router.get(
    "",
    response_model=list[DogInternalResponse],
    summary="List dogs",
    description="Retrieve a list of all dogs in the system.",
)
def list_dogs_route(db: Session = Depends(get_db)) -> list[DogInternalResponse]:
    try:
        dogs = list_dogs(db)
        return [DogInternalResponse.model_validate(dog) for dog in dogs]
    except DomainError as e:
        raise HTTPException(status_code=400, detail=e.issue.value)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=DogInternalResponse,
    summary="Create a dog",
    description="Create a new dog entry in the system.",
)
def create_dog_route(
    payload: DogCreateRequest,
    db: Session = Depends(get_db)
) -> DogInternalResponse:
    try:
        dog = create_dog(payload, db)
        return DogInternalResponse.model_validate(dog)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=e.issue.value)


@router.get(
    "/{dog_id}",
    response_model=DogInternalResponse,
    summary="Get dog",
    description="Retrieve a dog by ID.",
)
def get_dog_route(dog_id: str, db: Session = Depends(get_db)) -> DogInternalResponse:
    try:
        payload = DogRequest(dog_id=dog_id)
        dog = get_dog(payload, db)
        return DogInternalResponse.model_validate(dog)
    except DomainError as e:
        raise HTTPException(status_code=400, detail=e.issue.value)




