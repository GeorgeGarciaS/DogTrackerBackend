from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment variables Computed
    DB_URL: Optional[str] = None

    # Environment variables Required 
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    LOG_LEVEL: str

    @property
    def database_url(self) -> str:
        if self.DB_URL:
            return self.DB_URL
        return (
            f"postgresql+psycopg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    class Config:
        env_file = ".env"


settings = Settings() # type: ignore