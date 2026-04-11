import logging

from src.core.settings import settings


def setup_logging() -> None:
    logging.basicConfig(
        level=settings.LOG_LEVEL
    )