from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Valores padrão são substituídos por variáveis de ambiente ou arquivo .env
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    environment: str = "development"
    # Definição injetável do caminho do endpoint
    notify_route_path: str = "/api/v1/mailbox/{owner_id}/notify"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instância global (*Singleton*) de configuração: passar as infos apenas, e morrer.
settings = Settings()