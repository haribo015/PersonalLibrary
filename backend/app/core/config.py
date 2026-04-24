from pathlib import Path
from typing import Any

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    app_env: str = Field("development", env="APP_ENV")
    api_v1_str: str = Field("/api/v1", env="API_V1_STR")
    database_url: PostgresDsn = Field(..., env="DATABASE_URL")
    google_books_api_key: str = Field("", env="GOOGLE_BOOKS_API_KEY")
    secret_key: str = Field("change_me_to_a_secure_secret", env="SECRET_KEY")
    cors_allow_origins: str = Field(
        "http://localhost:4200,http://127.0.0.1:4200,http://localhost:9000,http://127.0.0.1:9000",
        env="CORS_ALLOW_ORIGINS",
    )

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_allow_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]


settings = Settings()
