"""Application configuration settings."""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Password Manager"
    port: int = 8005
    debug: bool = True

    # Security
    secret_key: str = "your-secret-key-change-in-production-use-environment-variable"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    # Encryption
    encryption_key: str = "your-encryption-key-change-in-production-use-32-byte-key"

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
