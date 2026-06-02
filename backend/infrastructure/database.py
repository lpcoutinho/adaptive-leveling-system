"""PostgreSQL connection e queries via floci RDS."""
import asyncpg
from backend.config import get_settings

_settings = get_settings()


async def get_db_connection():
    """
    Retorna conexão assíncrona com PostgreSQL.

    Returns:
        Connection: Conexão asyncpg
    """
    return await asyncpg.connect(_settings.database_url)


async def execute_query(query: str, *args, fetch: str = "all") -> list | None:
    """
    Executa query e retorna resultados.

    Args:
        query: SQL query string
        *args: Parâmetros da query
        fetch: Tipo de fetch ('all', 'one', 'val', None)

    Returns:
        Lista de resultados ou valor único
    """
    conn = await get_db_connection()
    try:
        if fetch == "all":
            return await conn.fetch(query, *args)
        elif fetch == "one":
            return await conn.fetchrow(query, *args)
        elif fetch == "val":
            return await conn.fetchval(query, *args)
        else:
            await conn.execute(query, *args)
            return None
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
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        return True
    except Exception as e:
        print(f"Database ping failed: {e}")
        return False
