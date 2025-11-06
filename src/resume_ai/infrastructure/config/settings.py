"""Application settings management."""

from functools import lru_cache
from typing import List

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Centralized configuration loaded from environment variables."""

    app_name: str = Field(default="Resume Intelligence API", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    app_port: int = Field(default=8000, alias="APP_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    allow_origins_raw: str = Field(default="*", alias="ALLOW_ORIGINS")

    mongodb_uri: str = Field(default="mongodb://localhost:27017/resume_ai", alias="MONGODB_URI")
    qdrant_url: HttpUrl = Field(default="http://localhost:6333", alias="QDRANT_URL")

    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4.1", alias="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-large", alias="OPENAI_EMBEDDING_MODEL"
    )

    ocr_language: str = Field(default="en", alias="OCR_LANGUAGE")
    ocr_use_gpu: bool = Field(default=False, alias="OCR_USE_GPU")
    ocr_model_dir: str | None = Field(default=None, alias="OCR_MODEL_DIR")

    vector_collection: str = Field(default="resumes", alias="VECTOR_COLLECTION")
    vector_similarity: str = Field(default="cosine", alias="VECTOR_SIMILARITY")
    vector_size: int = Field(default=3072, alias="VECTOR_SIZE")

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    @property
    def allow_origins(self) -> List[str]:
        """Return parsed list of allowed origins."""

        if not self.allow_origins_raw:
            return ["*"]
        return [item.strip() for item in self.allow_origins_raw.split(",") if item.strip()]


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return cached application settings."""
    return AppSettings()
