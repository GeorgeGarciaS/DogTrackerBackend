from src.api.schemas.dog import DogCreateRequest
from src.enums import DogErrorType
from src.validation.helpers import validate_latitude, validate_longitude


def validate_create_dog(payload: DogCreateRequest) -> list[str]:
    errors: list[str] = []

    if not (validate_latitude(payload.start_latitude)):
        errors.append(DogErrorType.INVALID_COORDINATES.value)

    if not (validate_longitude(payload.start_longitude)):
        errors.append(DogErrorType.INVALID_COORDINATES.value)
    return errors