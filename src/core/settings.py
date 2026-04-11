from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Environment variables Required 
    DB_HOST: str
    # DB_PORT: int
    # DB_NAME: str
    # DB_USER: str
    # DB_PASSWORD: str
    LOG_LEVEL: str

    class Config:
        env_file = ".env"


settings = Settings() # type: ignore