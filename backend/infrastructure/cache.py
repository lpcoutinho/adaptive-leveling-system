"""Valkey client via floci ElastiCache."""

from typing import Any, cast

import redis.asyncio as redis

from backend.config import get_settings

_settings = get_settings()
_client: redis.Redis | None = None


async def get_cache_client() -> redis.Redis:
    """
    Retorna cliente singleton para Valkey (Redis).

    Returns:
        redis.Redis: Cliente Redis assíncrono.
    """
    global _client
    if _client is None:
        _client = redis.from_url(_settings.redis_url, decode_responses=True)
    return _client


async def cache_set(key: str, value: Any, ttl: int | None = None) -> bool:
    """
    Armazena valor no cache.

    Args:
        key: Chave do cache.
        value: Valor a ser armazenado.
        ttl: Tempo de vida em segundos.

    Returns:
        bool: True se sucesso.
    """
    client = await get_cache_client()
    return cast(bool, await client.set(key, str(value), ex=ttl))


async def cache_get(key: str) -> str | None:
    """
    Recupera valor do cache.

    Args:
        key: Chave do cache.

    Returns:
        str | None: Valor armazenado ou None se não encontrado.
    """
    client = await get_cache_client()
    result = await client.get(key)
    return cast(str, result) if result is not None else None


async def cache_delete(key: str) -> bool:
    """
    Remove chave do cache.

    Args:
        key: Chave do cache.

    Returns:
        bool: True se sucesso.
    """
    client = await get_cache_client()
    return cast(int, await client.delete(key)) > 0


async def cache_increment(key: str) -> int:
    """
    Incrementa um contador no cache.

    Args:
        key: Chave do contador.

    Returns:
        int: Novo valor do contador.
    """
    client = await get_cache_client()
    return cast(int, await client.incr(key))


async def ping_cache() -> bool:
    """
    Testa conexão com Valkey.

    Returns:
        bool: True se saudável.
    """
    try:
        client = await get_cache_client()
        return cast(bool, await client.ping())
    except Exception as e:
        print(f"Cache ping failed: {e}")
        return False
