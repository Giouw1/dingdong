import logging.config
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV = os.getenv("APP_ENV", "development")
class EnvSettings(BaseSettings):
    IS_PRODUCTION: bool = False
    model_config = SettingsConfigDict(
        env_file=f".env.{ENV}",
        env_file_encoding="utf-8",
        extra="ignore"
    )

class NetworkSettings(BaseSettings):
    SERVER_HOST: str = "127.0.0.1"
    SERVER_PORT: int = 8000
    NOTIF_ROUTE_PATH: str = "/notifications"
    OWNER_ROUTE_PATH: str = "/owner"    
    model_config = SettingsConfigDict(
        env_file=f".env.{ENV}",
        env_prefix="NETWORK_",
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
        env_file=f".env.{ENV}",
        env_file_encoding="utf-8",
        extra="ignore"
    )
class LogSettings(BaseSettings):
    log_level: str = "DEBUG"
    max_retries: int = 3
    
    model_config = SettingsConfigDict(
        env_file=f".env.{ENV}",
        env_prefix="LOG_", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

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
    
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "standard",
                "level": settings.log_level.upper(),
            },
        },
        "root": {
            "handlers": ["console"],
            "level": settings.log_level.upper(),
        },
        "file": {
                "class": "logging.FileHandler",
                "filename": "execution.log",
                "formatter": "standard",
                "level": settings.log_level.upper(),
                "encoding": "utf-8",
                "mode": "w", # "a" for append, "w" for overwrite
            },
    }
    
    logging.config.dictConfig(LOGGING_CONFIG)