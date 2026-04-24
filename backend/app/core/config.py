from pathlib import Path
from typing import Any

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent.parent
LOCAL_DEV_SCHEME = "http"


def _build_local_origin(host: str, port: int) -> str:
    return f"{LOCAL_DEV_SCHEME}://{host}:{port}"


DEFAULT_CORS_ALLOW_ORIGINS = ",".join(
    [
        _build_local_origin("localhost", 4200),
        _build_local_origin("127.0.0.1", 4200),
        _build_local_origin("localhost", 9000),
        _build_local_origin("127.0.0.1", 9000),
    ]
)


class Settings(BaseSettings):
    app_env: str = Field("development", env="APP_ENV")
    api_v1_str: str = Field("/api/v1", env="API_V1_STR")
    database_url: PostgresDsn = Field(..., env="DATABASE_URL")
    google_books_api_key: str = Field("", env="GOOGLE_BOOKS_API_KEY")
    secret_key: str = Field("change_me_to_a_secure_secret", env="SECRET_KEY")
    cors_allow_origins: str = Field(
        DEFAULT_CORS_ALLOW_ORIGINS,
        env="CORS_ALLOW_ORIGINS",
    )

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"

    @property
    def cors_allow_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]


settings = Settings()
