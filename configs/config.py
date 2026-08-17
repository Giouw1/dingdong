import logging.config
import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict

#Gets the parameter of the environment, defaulting to 'development'
#Could be set through docker configuration, take a look at it when using dockers later.
ENV = os.getenv("APP_ENV", "development")
class OverallSettings(BaseSettings):
    IS_PRODUCTION: bool = False

class NetworkSettings(BaseSettings):
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    notify_route_path: str = "/api/v1/mailbox/{owner_id}/notify"
    
    model_config = SettingsConfigDict(
        env_file=f".env.{ENV}",
        env_prefix="NETWORK_",
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

"""Factory functions: to detach settings instantiation in import time, so that it is decided
    in runtime and can be overwritten by monkeypatches"""
#The idea is to make this get_network_settings be called by other functions. On my tests regarding network, monkeypatch it to be local.
@lru_cache
def get_network_settings() -> NetworkSettings:
    return NetworkSettings()

@lru_cache
def get_log_settings() -> LogSettings:
    return LogSettings()
def get_overall_settings()-> OverallSettings:
    return OverallSettings()

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