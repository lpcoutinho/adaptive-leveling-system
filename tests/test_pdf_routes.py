"""Testes de integração para as rotas de PDF."""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
def sample_pdf_path():
    return "tests/fixtures/calculus_1.pdf"


@pytest.mark.asyncio
async def test_upload_pdf_route(sample_pdf_path):
    """Testa o endpoint de upload de PDF."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with open(sample_pdf_path, "rb") as f:
            files = {"file": ("test.pdf", f, "application/pdf")}
            response = await ac.post("/api/v1/pdf/upload", files=files)

        assert response.status_code == 201, f"Upload falhou: {response.text}"
        data = response.json()
        assert "id" in data
        assert "hash" in data

    assert "id" in data
    assert "hash" in data


@pytest.mark.asyncio
async def test_get_pdf_route(sample_pdf_path):
    """Testa recuperação de metadados de PDF."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Primeiro faz o upload
        with open(sample_pdf_path, "rb") as f:
            files = {"file": ("test_get.pdf", f, "application/pdf")}
            up_res = await ac.post("/api/v1/pdf/upload", files=files)

        pdf_id = up_res.json()["id"]

        # Depois recupera
        response = await ac.get(f"/api/v1/pdf/{pdf_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == pdf_id
    assert data["filename"] == "test_get.pdf"
    assert "content_text" in data
