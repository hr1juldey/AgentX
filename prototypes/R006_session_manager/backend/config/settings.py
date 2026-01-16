"""Application configuration settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "Session Manager"
    version: str = "0.1.0"
    port: int = 8006
    debug: bool = True

    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_max_connections: int = 10
    redis_socket_timeout: int = 5
    redis_socket_connect_timeout: int = 5

    # Session Configuration
    session_expiry_hours: int = 24
    session_token_length: int = 64

    # CORS
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
