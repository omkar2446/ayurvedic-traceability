from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "medguard"
    app_env: str = "development"
    database_url: str = "sqlite:///./medguard.db"
    postgres_db: str = "medguard"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    backend_port: int = 8000
    backend_cors_origins: str = "http://localhost:5173"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    fabric_network: str = ""
    fabric_channel: str = ""
    fabric_chaincode: str = ""
    fabric_msp_id: str = ""
    fabric_cert_path: str = ""
    fabric_key_path: str = ""
    fabric_tls_cert_path: str = ""
    storage_path: str = "./storage/documents"
    max_upload_size: int = 10485760

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
