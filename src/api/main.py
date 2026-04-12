from fastapi import FastAPI
from contextlib import asynccontextmanager

from src.api.routes.analytics import router as analytics_router
from src.api.routes.dogs import router as dogs_router
from src.api.routes.health import router as health_router
from src.api.routes.internal.dogs import router as internal_dogs_router
from src.core.logging import setup_logging
from src.db.session import Base, engine


setup_logging()

api = FastAPI(
    title="DogTracker Backend",
    version="0.1.0",
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    Base.metadata.create_all(bind=engine)
    yield
    # shutdown
    return

api.include_router(health_router)
api.include_router(dogs_router)
api.include_router(analytics_router)
api.include_router(internal_dogs_router)
