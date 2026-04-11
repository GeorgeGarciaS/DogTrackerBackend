from src.api.schemas.health import HealthResponse


def health_check() -> HealthResponse:
    return HealthResponse(
        status="ok"
    )