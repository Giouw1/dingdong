import logging.config
import logging.handlers
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AliasChoices, Field, field_validator
from typing import Any
from pathlib import Path
ENV = os.getenv(key="APP_ENV", default="example")
class EnvSettings(BaseSettings):
    IS_PRODUCTION: bool = False
    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{ENV}"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

class NetworkSettings(BaseSettings):
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000
    NOTIF_ROUTE_PATH: str = "/notifications"
    OWNER_ROUTE_PATH: str = "/owner"
    ALLOWED_ORIGINS: list[str] | str = Field(
        default=[
            "http://localhost:8000",
            "http://127.0.0.1:8000",
            "http://localhost:5500",
            "http://127.0.0.1:5500",
        ],
        validation_alias=AliasChoices("ALLOWED_ORIGINS", "NETWORK_ALLOWED_ORIGINS", "allowed_origins")
    )

    @field_validator("ALLOWED_ORIGINS", mode="after")
    @classmethod
    def parse_allowed_origins(cls, v: Any) -> list[str]:
        if isinstance(v, str):
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                import json
                return json.loads(v)
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{ENV}"),
        env_file_encoding="utf-8",
        extra="ignore"
    )
class DatabaseSettings(BaseSettings):
    IN_MEMORY: bool = True
    SQLite3: bool = False
    MAILBOX_DB_NAME: str = "mailbox"
    OWNERREPO_DB_NAME: str = "ownerrepo"
    MAILBOX_DB_PATH: str = "databases"
    OWNERREPO_DB_PATH: str = "databases"
    DB_PATH: str = "databases/app.db"
    
    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{ENV}"),
        env_file_encoding="utf-8",
        extra="ignore"
    )
class LogSettings(BaseSettings):
    log_level: str = Field(default="INFO", validation_alias=AliasChoices("LOG_LEVEL", "log_level", "LOG_LOG_LEVEL"))
    max_retries: int = Field(default=3, validation_alias=AliasChoices("MAX_RETRIES", "max_retries", "LOG_MAX_RETRIES"))
    LOG_DIR: Path = Field(default=Path("data/logging"), validation_alias=AliasChoices("LOG_DIR", "log_dir", "LOG_LOG_DIR"))
    LOG_FILE: str = Field(default="network.log", validation_alias=AliasChoices("LOG_FILE", "log_file", "LOG_LOG_FILE"))
    MAX_BYTES: int = Field(default=10 * 1024 * 1024, validation_alias=AliasChoices("MAX_BYTES", "max_bytes", "LOG_MAX_BYTES"))
    BACKUP_COUNT: int = Field(default=5, validation_alias=AliasChoices("BACKUP_COUNT", "backup_count", "LOG_BACKUP_COUNT"))
    
    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{ENV}"),
        env_prefix="LOG_", 
        env_file_encoding="utf-8",
        extra="ignore"
    )
class FrontendSettings(BaseSettings):
    FRONTEND_PATH: Path = Path("data/frontend")

    model_config = SettingsConfigDict(
        env_file=(".env", f".env.{ENV}"),
        env_file_encoding="utf-8",
        extra="ignore"
    )
@lru_cache
def get_frontend_settings() -> FrontendSettings:
    return FrontendSettings()

@lru_cache
def get_network_settings() -> NetworkSettings:
    return NetworkSettings()

@lru_cache
def get_log_settings() -> LogSettings:
    return LogSettings()

@lru_cache
def get_db_settings()-> DatabaseSettings:
    return DatabaseSettings()

@lru_cache
def get_env_settings()-> EnvSettings:
    return EnvSettings()


def setup_logging() -> None:
    """
    Constructs the logging schema at execution time.
    Retrieves configuration via the factory function to ensure 
    compatibility with pytest mocking structures.
    """
    settings = get_log_settings()
    
    base_dir = Path(__file__).resolve().parent.parent
    log_dir = settings.LOG_DIR if settings.LOG_DIR.is_absolute() else (base_dir / settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file_path = log_dir / settings.LOG_FILE
    
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
            "network": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": settings.log_level.upper(),
            },
            "network_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(log_file_path),
                "formatter": "network",
                "level": settings.log_level.upper(),
                "encoding": "utf-8",
                "maxBytes": settings.MAX_BYTES,
                "backupCount": settings.BACKUP_COUNT,
            },
        },
        "loggers": {
            "network": {
                "handlers": ["network_file", "console"],
                "level": settings.log_level.upper(),
                "propagate": False,
            },
        },
        "root": {
            "handlers": ["console"],
            "level": settings.log_level.upper(),
        },
    }
    
    logging.config.dictConfig(LOGGING_CONFIG)