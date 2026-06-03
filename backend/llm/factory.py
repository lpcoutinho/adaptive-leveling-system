"""Factory para criação de instâncias de LLM providers."""

from backend.llm.base.interface import ILLMProvider
from backend.llm.config import get_llm_settings
from backend.llm.providers.groq_provider import GroqProvider
from backend.llm.providers.mock_provider import MockProvider

_settings = get_llm_settings()


class LLMFactory:
    """Factory para gerenciar instâncias de providers de LLM."""

    @staticmethod
    def get_provider() -> ILLMProvider:
        """
        Retorna o provider configurado.

        Returns:
            ILLMProvider: Instância do provider.
        """
        provider_name = _settings.llm_provider.lower()

        if provider_name == "groq":
            return GroqProvider()
        elif provider_name == "mock":
            return MockProvider()
        else:
            raise ValueError(f"Provider de LLM desconhecido: {provider_name}")

    @staticmethod
    def is_configured() -> bool:
        """
        Verifica se o provider atual possui as credenciais necessárias.

        Returns:
            bool: True se configurado corretamente.
        """
        provider_name = _settings.llm_provider.lower()

        if provider_name == "mock":
            return True
        if provider_name == "groq":
            return bool(_settings.groq_api_key and len(_settings.groq_api_key) > 10)

        return False
