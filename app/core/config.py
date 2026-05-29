from functools import lru_cache
from typing import Annotated

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Environment-driven application configuration."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Multi-Agent Business Automation"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    secret_key: Annotated[str, Field(min_length=16)] = "change-me-in-production"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/automation_db"
    redis_url: str = "redis://localhost:6379/0"
    celery_broker_url: str | None = None
    celery_result_backend: str | None = None

    openai_api_key: str | None = None
    cors_origins: list[AnyHttpUrl] | list[str] = ["http://localhost:3000", "http://localhost:8000"]
    rate_limit_per_minute: int = 120
    log_level: str = "INFO"
    enable_ai_frameworks: bool = True

    @field_validator("database_url", mode="before")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+asyncpg://", 1)
        return value

    @property
    def sync_database_url(self) -> str:
        return self.database_url.replace("postgresql+asyncpg://", "postgresql://", 1)

    @property
    def broker_url(self) -> str:
        return self.celery_broker_url or self.redis_url

    @property
    def result_backend_url(self) -> str:
        return self.celery_result_backend or self.redis_url


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

