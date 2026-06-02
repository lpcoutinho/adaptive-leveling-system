"""Configuração do frontend Streamlit."""
import os
from pydantic_settings import BaseSettings


class FrontendSettings(BaseSettings):
    """Configurações do frontend."""
    
    api_url: str = "http://localhost:8000"
    app_title: str = "Adaptive Leveling System"


def get_frontend_settings() -> FrontendSettings:
    """Retorna configurações do frontend."""
    return FrontendSettings()
