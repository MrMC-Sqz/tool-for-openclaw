from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OpenClaw Skill Explorer + Risk Scanner API"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    database_url: str = "sqlite:///./openclaw_skill_explorer.db"
    db_pool_pre_ping: bool = True
    cache_enabled: bool = True
    cache_ttl_seconds: int = 30
    auth_enabled: bool = False
    auth_api_keys: str = ""
    github_token: str | None = None
    openai_api_key: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-5.4-mini"
    openai_fallback_model: str = "gpt-5.3"
    openai_timeout_seconds: int = 15
    cors_allow_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("cors_allow_origins", mode="before")
    @classmethod
    def _parse_cors_allow_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return []

    @field_validator("database_url", mode="before")
    @classmethod
    def _normalize_database_url(cls, value: str) -> str:
        if not isinstance(value, str):
            return value
        normalized = value.strip()
        if normalized.startswith("postgres://"):
            return normalized.replace("postgres://", "postgresql+psycopg://", 1)
        if normalized.startswith("postgresql://"):
            return normalized.replace("postgresql://", "postgresql+psycopg://", 1)
        return normalized

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
