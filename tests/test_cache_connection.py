"""Testes de conexão Valkey via floci ElastiCache."""
import pytest


@pytest.mark.asyncio
class TestValkeyConnection:
    """Testes de conexão com Valkey."""

    async def test_cache_connection_successful(self):
        """Testa que conexão com Valkey é estabelecida."""
        from backend.infrastructure.cache import get_cache_client

        client = await get_cache_client()
        assert client is not None
        await client.aclose()

    async def test_cache_set_and_get(self):
        """Testa set/get no cache."""
        from backend.infrastructure.cache import cache_set, cache_get

        await cache_set("test_key", "test_value", ttl=60)
        value = await cache_get("test_key")
        assert value == "test_value"

        # Limpar
        from backend.infrastructure.cache import cache_delete
        await cache_delete("test_key")

    async def test_cache_delete(self):
        """Testa delete no cache."""
        from backend.infrastructure.cache import cache_set, cache_get, cache_delete

        await cache_set("delete_me", "value", ttl=60)
        await cache_delete("delete_me")
        value = await cache_get("delete_me")
        assert value is None

    async def test_cache_ping(self):
        """Testa ping no cache retorna sucesso."""
        from backend.infrastructure.cache import ping_cache

        is_healthy = await ping_cache()
        assert is_healthy is True
