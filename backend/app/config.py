from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # database connection strings — async for the api, sync for celery workers
    database_url: str = "postgresql+asyncpg://erebys:erebys_secret@postgres:5432/erebys"
    database_url_sync: str = "postgresql://erebys:erebys_secret@postgres:5432/erebys"

    # redis urls
    redis_url: str = "redis://redis:6379/0"

    # jwt config — change the secret in production, seriously
    jwt_secret: str = "change-me-to-a-real-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7

    # general app settings
    environment: str = "development"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:3000"

    # celery broker and result backend
    celery_broker_url: str = "redis://redis:6379/1"
    celery_result_backend: str = "redis://redis:6379/2"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    model_config = {"env_file": ".env", "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
