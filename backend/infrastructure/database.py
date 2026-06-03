"""PostgreSQL connection e queries via floci RDS."""

from typing import Any, cast

import asyncpg
from loguru import logger

from backend.config import get_settings

_settings = get_settings()


async def get_db_connection():
    """
    Estabelece conexão assíncrona com PostgreSQL.

    Returns:
        asyncpg.Connection: Objeto de conexão.
    """
    return await asyncpg.connect(_settings.database_url)


async def execute_query(query: str, *args: Any) -> list[Any] | None:
    """
    Executa uma query no banco de dados e retorna os resultados.

    Args:
        query: A string SQL a ser executada.
        *args: Argumentos para a query.

    Returns:
        list[Any] | None: Lista de registros ou None para comandos sem retorno.
    """
    conn = await get_db_connection()
    try:
        query_upper = query.strip().upper()
        # Se a query retorna resultados (SELECT ou RETURNING), usamos fetch
        if query_upper.startswith("SELECT") or "RETURNING" in query_upper:
            return cast(list[Any], await conn.fetch(query, *args))
        else:
            await conn.execute(query, *args)
            return None
    except Exception as e:
        logger.error(f"Erro ao executar query SQL: {e}\nQuery: {query}")
        raise e
    finally:
        await conn.close()


async def ping_database() -> bool:
    """
    Testa conexão com PostgreSQL.

    Returns:
        bool: True se conexão está saudável
    """
    try:
        conn = await get_db_connection()
        await conn.fetchval("SELECT version()")
        await conn.close()
        return True
    except Exception as e:
        logger.warning(f"Database ping failed: {e}")
        return False
