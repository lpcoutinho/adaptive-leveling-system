"""Configuração para os providers de LLM."""
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    """Configurações de LLM via environment variables."""

    llm_provider: str = "mock"
    llm_primary_model: str = "llama-3.3-70b"
    llm_fallback_model: str = "deepseek-r1"

    # API Keys
    groq_api_key: str = ""
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    # Resilience
    llm_timeout: int = 30
    llm_max_retries: int = 3

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


def get_llm_settings() -> LLMSettings:
    """Retorna instância singleton das configurações de LLM."""
    return LLMSettings()
