"""Testes de integração para endpoints de avaliação."""

from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app

pytestmark = pytest.mark.usefixtures("clean_database")


@pytest.fixture
def sample_pdf_path():
    return "tests/fixtures/calculus_1.pdf"


@pytest.mark.asyncio
async def test_generate_assessment_no_prerequisites(sample_pdf_path):
    """POST /assessment/generate/{pdf_id} sem pré-requisitos retorna 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with open(sample_pdf_path, "rb") as f:
            files = {"file": ("calc.pdf", f, "application/pdf")}
            up_res = await ac.post("/api/v1/pdf/upload", files=files)
        pdf_id = up_res.json()["id"]

        response = await ac.post(f"/api/v1/assessment/generate/{pdf_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_assessment_not_found():
    """GET /assessment/{id} para ID inexistente retorna 404."""
    transport = ASGITransport(app=app)
    fake_id = uuid4()
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/assessment/{fake_id}")

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_assessment_by_pdf_not_found():
    """GET /assessment/pdf/{pdf_id} sem avaliação retorna 404."""
    transport = ASGITransport(app=app)
    fake_id = uuid4()
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/assessment/pdf/{fake_id}")

    assert response.status_code == 404
