"""Testes unitários para o serviço de processamento de PDF."""

import pytest

from backend.services.pdf_service import calculate_hash, extract_text_from_pdf, process_pdf


@pytest.fixture
def sample_pdf_content():
    """Lê o conteúdo do PDF de teste."""
    path = "tests/fixtures/calculus_1.pdf"
    with open(path, "rb") as f:
        return f.read()


def test_calculate_hash():
    """Testa que o hash é consistente."""
    content = b"test content"
    hash1 = calculate_hash(content)
    hash2 = calculate_hash(content)
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex length


def test_extract_text_from_pdf(sample_pdf_content):
    """Testa a extração de texto do PDF real."""
    text = extract_text_from_pdf(sample_pdf_content)
    assert isinstance(text, str)
    assert len(text) > 0
    # Verifica termos conhecidos no PDF de Cálculo I
    assert "Limite" in text or "limite" in text or "Cálculo" in text


@pytest.mark.asyncio
async def test_process_pdf_idempotency(sample_pdf_content):
    """Testa que processar o mesmo PDF duas vezes retorna o mesmo registro."""
    filename = "test.pdf"

    # Primeiro processamento
    doc1 = await process_pdf(sample_pdf_content, filename)
    assert doc1.id is not None

    # Segundo processamento (deve reusar)
    doc2 = await process_pdf(sample_pdf_content, filename)

    assert doc1.id == doc2.id
    assert doc1.hash == doc2.hash
