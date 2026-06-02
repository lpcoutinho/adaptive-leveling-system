"""Testes para interface ILLMProvider."""
import pytest
from pydantic import BaseModel
from backend.llm.base.interface import ILLMProvider


class DummyResponse(BaseModel):
    """Modelo de resposta dummy para testes."""
    message: str


class DummyProvider(ILLMProvider):
    """Implementação dummy para testes."""

    async def generate_structured(self, prompt: str, response_model: type) -> BaseModel:
        """Gera resposta estruturada dummy."""
        return response_model(message="dummy response")

    async def generate_text(self, prompt: str) -> str:
        """Gera texto dummy."""
        return "dummy text"

    def get_provider_name(self) -> str:
        """Retorna nome do provider."""
        return "dummy"


@pytest.mark.asyncio
class TestILLMProvider:
    """Testes da interface ILLMProvider."""

    async def test_concrete_provider_must_implement_all_methods(self):
        """Testa que provider concreto implementa todos os métodos abstratos."""
        provider = DummyProvider()

        assert hasattr(provider, 'generate_structured')
        assert hasattr(provider, 'generate_text')
        assert hasattr(provider, 'get_provider_name')

    async def test_generate_structured_returns_correct_type(self):
        """Testa que generate_structured retorna o modelo esperado."""
        provider = DummyProvider()
        result = await provider.generate_structured("test", DummyResponse)

        assert isinstance(result, DummyResponse)
        assert result.message == "dummy response"

    async def test_generate_text_returns_string(self):
        """Testa que generate_text retorna string."""
        provider = DummyProvider()
        result = await provider.generate_text("test")

        assert isinstance(result, str)
        assert result == "dummy text"

    async def test_get_provider_name_returns_string(self):
        """Testa que get_provider_name retorna nome do provider."""
        provider = DummyProvider()
        name = provider.get_provider_name()

        assert isinstance(name, str)
        assert name == "dummy"
