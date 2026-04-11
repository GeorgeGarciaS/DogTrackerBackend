from re import I

from fastapi import APIRouter

from src.api.schemas.health import HealthResponse
from src.services.health_service import health_check

router = APIRouter(tags=["health"])


@router.get("/health")
def health_check_route() -> HealthResponse:
    return health_check()