from functools import lru_cache
from pathlib import Path

from pydantic import Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables."""

    app_name: str = Field(default="LegalLens AI", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:3000"],
        alias="CORS_ORIGINS",
    )
    document_storage_dir: Path = Field(
        default=Path(__file__).resolve().parents[1] / "storage" / "documents",
        alias="DOCUMENT_STORAGE_DIR",
    )
    max_pdf_upload_bytes: int = Field(
        default=10 * 1024 * 1024,
        alias="MAX_PDF_UPLOAD_BYTES",
    )
    min_extractable_text_chars: int = Field(
        default=20,
        alias="MIN_EXTRACTABLE_TEXT_CHARS",
    )
    gemini_api_keys: list[SecretStr] | None = Field(
        default=None,
        alias="GEMINI_API_KEYS",
        repr=False,
    )
    groq_api_key: SecretStr | None = Field(
        default=None,
        alias="GROQ_API_KEY",
        repr=False,
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    @field_validator("gemini_api_keys", mode="before")
    @classmethod
    def parse_gemini_api_keys(cls, value: str | list[str]) -> list[SecretStr]:
        if not value:
            return []
        if isinstance(value, str):
            # Split by comma and clean whitespace
            return [SecretStr(key.strip()) for key in value.split(",") if key.strip()]
        if isinstance(value, list):
            return [SecretStr(key) if isinstance(key, str) else key for key in value]
        return value

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("max_pdf_upload_bytes", "min_extractable_text_chars")
    @classmethod
    def validate_positive_int(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("value must be greater than zero")
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
