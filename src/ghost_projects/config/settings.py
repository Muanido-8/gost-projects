
from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Ghost Projects"
    debug: bool = False

    ollama_base_url: str = "http://localhost:11434/v1"
    ollama_api_key: SecretStr = SecretStr("ollama")
    model_name: str = "gemma4:31b"

    max_file_size_bytes: int = Field(
        default=500_000,
        gt=0,
    )
    max_files_per_scan: int = Field(
        default=2_000,
        gt=0,
    )
    max_file_content_chars: int = Field(
        default=20_000,
        gt=0,
    )


settings = Settings()
