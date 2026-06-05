"""Testes de integração para as rotas de pré-requisitos."""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
def sample_pdf_path():
    return "tests/fixtures/calculus_1.pdf"


@pytest.mark.asyncio
async def test_extract_prerequisites_route(sample_pdf_path):
    """Testa o endpoint de extração de pré-requisitos."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Primeiro faz upload do PDF
        with open(sample_pdf_path, "rb") as f:
            files = {"file": ("calculus.pdf", f, "application/pdf")}
            up_res = await ac.post("/api/v1/pdf/upload", files=files)

        assert up_res.status_code == 201
        pdf_id = up_res.json()["id"]

        # Depois solicita extração
        response = await ac.post(f"/api/v1/prerequisites/extract/{pdf_id}")

    assert response.status_code == 201
    data = response.json()
    assert "main_concepts" in data
    assert "prerequisites" in data
    assert data["pdf_id"] == pdf_id


@pytest.mark.asyncio
async def test_extract_prerequisites_invalid_pdf():
    """Testa extração com PDF inexistente."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/prerequisites/extract/00000000-0000-0000-0000-000000000000"
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_prerequisites_not_found():
    """Testa consulta de pré-requisitos antes da extração."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/v1/prerequisites/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_prerequisites_after_extraction(sample_pdf_path):
    """Testa recuperação de pré-requisitos após extração."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Upload
        with open(sample_pdf_path, "rb") as f:
            files = {"file": ("calc.pdf", f, "application/pdf")}
            up_res = await ac.post("/api/v1/pdf/upload", files=files)

        assert up_res.status_code == 201, f"Upload falhou: {up_res.text}"
        data = up_res.json()
        assert "id" in data, f"Resposta de upload incompleta: {data}"
        pdf_id = data["id"]
        # Extração
        ext_res = await ac.post(f"/api/v1/prerequisites/extract/{pdf_id}")
        assert ext_res.status_code == 201
        ext_data = ext_res.json()
        assert "id" in ext_data, f"Extract response missing id: {ext_data}"

        # Recuperação
        response = await ac.get(f"/api/v1/prerequisites/{pdf_id}")

    assert response.status_code == 200, f"GET failed: {response.text}"
    data = response.json()
    assert "main_concepts" in data
    assert "prerequisites" in data
    assert data["pdf_id"] == pdf_id
