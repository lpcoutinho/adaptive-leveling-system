"""Implementação de mock para provedor de LLM."""

from typing import Any, TypeVar

from pydantic import BaseModel

from backend.llm.base.interface import ILLMProvider

T = TypeVar("T", bound=BaseModel)


class MockProvider(ILLMProvider):
    """Provider de mock para testes e desenvolvimento offline."""

    def __init__(self):
        self._responses: dict[str, Any] = {}

    def set_response(self, prompt_part: str, response: Any):
        """Define uma resposta para um trecho de prompt."""
        self._responses[prompt_part] = response

    async def generate_structured(self, prompt: str, response_model: type[T]) -> T:
        """Retorna uma resposta estruturada de mock."""
        for part, resp in self._responses.items():
            if part in prompt:
                if isinstance(resp, response_model):
                    return resp
                return response_model.model_validate(resp)

        # Se não houver match, tenta criar uma instância válida com campos obrigatórios vazios
        # Isso evita erros de 'NoneType' ao acessar listas no serviço
        try:
            return response_model()
        except Exception:
            # Fallback para construct se o init falhar (menos seguro)
            return response_model.model_construct()

    async def generate_text(self, prompt: str) -> str:
        """Retorna um texto de mock."""
        for part, resp in self._responses.items():
            if part in prompt:
                return str(resp)
        return "Mock response for prompt"

    def get_provider_name(self) -> str:
        """Retorna o nome do provider."""
        return "mock"
