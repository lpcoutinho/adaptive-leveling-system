"""Valkey client via floci ElastiCache."""
import redis.asyncio as redis
from backend.config import get_settings

_settings = get_settings()
_client: redis.Redis | None = None


async def get_cache_client() -> redis.Redis:
    """
    Retorna cliente Valkey (Redis-compatible).

    Returns:
        redis.Redis: Cliente assíncrono Valkey
    """
    global _client
    if _client is None:
        _client = redis.Redis.from_url(
            _settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
    return _client


async def cache_set(key: str, value: str | int | float, ttl: int = 3600) -> None:
    """
    Define valor no cache.

    Args:
        key: Chave do cache
        value: Valor a armazenar
        ttl: Time to live em segundos (default 3600)
    """
    client = await get_cache_client()
    await client.set(key, value, ex=ttl)


async def cache_get(key: str) -> str | None:
    """
    Obtém valor do cache.

    Args:
        key: Chave do cache

    Returns:
        Valor ou None se não existir
    """
    client = await get_cache_client()
    return await client.get(key)


async def cache_delete(key: str) -> int | None:
    """
    Remove valor do cache.

    Args:
        key: Chave a deletar

    Returns:
        Número de chaves deletadas
    """
    client = await get_cache_client()
    return await client.delete(key)


async def ping_cache() -> bool:
    """
    Testa conexão com Valkey.

    Returns:
        bool: True se conexão está saudável
    """
    try:
        client = await get_cache_client()
        response = await client.ping()
        return response is True
    except Exception as e:
        print(f"Cache ping failed: {e}")
        return False
