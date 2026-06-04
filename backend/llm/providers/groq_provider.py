"""Implementação do provider Groq."""

from typing import TypeVar

from groq import AsyncGroq
from loguru import logger
from pydantic import BaseModel, ValidationError

from backend.llm.base.interface import ILLMProvider
from backend.llm.config import get_llm_settings

T = TypeVar("T", bound=BaseModel)
_settings = get_llm_settings()


class GroqProvider(ILLMProvider):
    """Provider para a API do Groq."""

    def __init__(self):
        self.client = AsyncGroq(api_key=_settings.groq_api_key)

    async def generate_structured(self, prompt: str, response_model: type[T]) -> T:
        """Gera resposta estruturada via Groq (usando tool calling ou JSON mode)."""
        try:
            completion = await self.client.chat.completions.create(
                model=_settings.llm_primary_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            content = completion.choices[0].message.content
            if content is None:
                raise ValueError("Groq returned empty content")
            return response_model.model_validate_json(content)
        except ValidationError as e:
            logger.error(
                f"Erro de validação Groq: {e}. "
                f"Conteúdo retornado: {content if 'content' in locals() else 'N/A'}"
            )
            raise
        except Exception as e:
            logger.error(f"Erro ao chamar Groq: {e}")
            raise

    async def generate_text(self, prompt: str) -> str:
        """Gera texto simples via Groq."""
        completion = await self.client.chat.completions.create(
            model=_settings.llm_primary_model,
            messages=[{"role": "user", "content": prompt}],
        )
        content = completion.choices[0].message.content
        return str(content) if content is not None else ""

    def get_provider_name(self) -> str:
        """Retorna o nome do provider."""
        return "groq"

    @property
    def model(self) -> str:
        """Retorna o modelo usado."""
        return _settings.llm_primary_model
