from sqlalchemy.orm import Session

from src.api.exceptions import DomainError
from src.api.schemas.dog import DogCreateRequest, DogCurrentStatusRequest, DogRequest
from src.db.models.dog import DogModel
from src.db.models.dog_current_status import DogCurrentStatusModel
from src.db.repositories.dog_current_status_repo import get_dog_current_status_by_id
from src.db.repositories.dog_repo import (
    create_dog_record,
    get_dog_by_id,
    get_dog_records,
)
from src.enums import DogErrorType
from src.validation.dog_validation import validate_create_dog


def list_dogs(db: Session) -> list[DogModel]:
    return get_dog_records(db)

def create_dog(payload: DogCreateRequest, db: Session) -> DogModel:
    errors = validate_create_dog(payload)
    if not (errors == []):
        if DogErrorType.INVALID_COORDINATES.value in errors:
            raise DomainError(DogErrorType.INVALID_COORDINATES)

    dog = DogModel(
        name=payload.name,
        start_latitude=payload.start_latitude,
        start_longitude=payload.start_longitude,
    )
    return create_dog_record(dog, db)

def get_dog(payload: DogRequest, db: Session) -> DogModel:
    dog = get_dog_by_id(payload.dog_id, db)
    if dog is None:
        raise DomainError(DogErrorType.DOG_NOT_FOUND)
    return dog

def get_dog_current_status(
    payload: DogCurrentStatusRequest,
    db: Session
) -> DogCurrentStatusModel:
    dog_current_status = get_dog_current_status_by_id(payload.dog_id, db)
    if dog_current_status is None:
        raise DomainError(DogErrorType.DOG_NOT_FOUND)
    return dog_current_status