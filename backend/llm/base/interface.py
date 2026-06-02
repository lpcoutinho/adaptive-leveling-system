"""Interface para os providers de LLM."""
from abc import ABC, abstractmethod
from typing import Type, TypeVar
from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)

class ILLMProvider(ABC):
    """Interface abstrata que define o contrato para todos os providers de LLM."""

    @abstractmethod
    async def generate_structured(self, prompt: str, response_model: Type[T]) -> T:
        """
        Gera uma resposta estruturada baseada em um modelo Pydantic.

        Args:
            prompt: O comando para o LLM.
            response_model: A classe Pydantic para estruturar a resposta.

        Returns:
            T: Uma instância do modelo Pydantic preenchida.
        """
        pass

    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """
        Gera uma resposta em texto simples.

        Args:
            prompt: O comando para o LLM.

        Returns:
            str: A resposta em texto puro.
        """
        pass

    @abstractmethod
    def get_provider_name(self) -> str:
        """
        Retorna o nome identificador do provider.

        Returns:
            str: O nome do provider (ex: 'groq', 'openai').
        """
        pass
