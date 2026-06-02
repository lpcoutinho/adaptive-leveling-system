"""Dependências FastAPI para LLM."""

from backend.llm.base.interface import ILLMProvider
from backend.llm.factory import LLMFactory


def get_llm_provider() -> ILLMProvider:
    """
    Dependency injection para o LLM Provider.

    Returns:
        ILLMProvider: O provider configurado.
    """
    return LLMFactory.get_provider()
