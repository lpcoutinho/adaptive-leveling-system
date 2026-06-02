"""Fixtures pytest para testes."""

import asyncio
import os

import pytest


@pytest.fixture(scope="session")
def event_loop():
    """Cria event loop para testes assíncronos."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def clean_database():
    """Limpa as tabelas do banco de dados antes de cada teste."""
    from backend.infrastructure.database import execute_query

    await execute_query("TRUNCATE TABLE pdf_documents CASCADE")
    yield


@pytest.fixture
def test_settings():
    """Configurações para testes."""
    os.environ.setdefault(
        "DATABASE_URL", "postgresql://postgres:postgres@127.0.0.1:5435/postgres?sslmode=disable"
    )
    os.environ.setdefault("REDIS_URL", "redis://127.0.0.1:6385/0")
    os.environ.setdefault("S3_ENDPOINT_URL", "http://127.0.0.1:9005")
    os.environ.setdefault("AWS_ACCESS_KEY_ID", "minioadmin")
    os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "minioadmin")
    os.environ.setdefault("LLM_PROVIDER", "mock")
    from backend.config import get_settings

    return get_settings()
