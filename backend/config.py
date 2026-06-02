"""Configuração centralizada da aplicação."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configurações da aplicação via environment variables."""

    # Application
    app_name: str = "Adaptive Leveling System"
    app_version: str = "0.1.0"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database (PostgreSQL)
    database_url: str = "postgresql://postgres:postgres@127.0.0.1:5435/postgres?sslmode=disable"

    # Cache (Valkey)
    redis_url: str = "redis://127.0.0.1:6385/0"

    # Storage (S3/Minio)
    aws_access_key_id: str = "minioadmin"
    aws_secret_access_key: str = "minioadmin"
    aws_region: str = "us-east-1"
    s3_endpoint_url: str = "http://127.0.0.1:9005"
    s3_bucket: str = "als-documents"

    # LLM Configuration
    llm_provider: str = "mock"
    llm_primary_model: str = "llama-3.3-70b"
    llm_fallback_model: str = "deepseek-r1"

    # API Keys (configure para providers reais)
    groq_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # LLM Resilience
    llm_timeout: int = 30
    llm_max_retries: int = 3
    llm_retry_delay: float = 1.0
    llm_circuit_breaker_threshold: int = 5
    llm_circuit_breaker_timeout: int = 60

    # OpenTelemetry
    otel_exporter_otlp_endpoint: str = "http://localhost:4318"
    otel_service_name: str = "adaptive-leveling-system"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


def get_settings() -> Settings:
    """Retorna instância singleton das configurações da aplicação."""
    settings = Settings()
    # print(f"DEBUG: DATABASE_URL={settings.database_url}") # Descomente para testar
    return settings
