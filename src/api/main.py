from fastapi import FastAPI

from src.api.routes.analytics import router as analytics_router
from src.api.routes.dogs import router as dogs_router
from src.api.routes.health import router as health_router
from src.core.logging import setup_logging


setup_logging()

api = FastAPI(
    title="DogTracker Backend",
    version="0.1.0",
)

api.include_router(health_router)
api.include_router(dogs_router)
api.include_router(analytics_router)
