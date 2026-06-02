"""Testes para os endpoints de health check."""
import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.mark.asyncio
async def test_health_check_basic():
    """Testa o endpoint básico de health check."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_detailed():
    """Testa o endpoint detalhado de health check."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/health/detailed")
    assert response.status_code == 200
    data = response.json()
    assert "api" in data
    assert "database" in data
    assert "cache" in data
    assert "storage" in data
    assert "llm_provider" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Testa o endpoint raiz."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]
