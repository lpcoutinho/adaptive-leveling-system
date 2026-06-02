"""Testes de conexão PostgreSQL via floci RDS."""
import pytest
import asyncpg


@pytest.mark.asyncio
class TestPostgreSQLConnection:
    """Testes de conexão com PostgreSQL."""

    async def test_database_connection_successful(self):
        """Testa que conexão com PostgreSQL é estabelecida."""
        from backend.config import get_settings
        settings = get_settings()

        conn = await asyncpg.connect(settings.database_url)
        assert conn is not None
        await conn.close()

    async def test_database_query_executes(self):
        """Testa que query simples executa com sucesso."""
        from backend.config import get_settings
        from backend.infrastructure.database import execute_query

        settings = get_settings()
        result = await execute_query("SELECT 1 as value")
        assert result[0]["value"] == 1

    async def test_database_ping(self):
        """Testa ping no banco retorna sucesso."""
        from backend.infrastructure.database import ping_database

        is_healthy = await ping_database()
        assert is_healthy is True
