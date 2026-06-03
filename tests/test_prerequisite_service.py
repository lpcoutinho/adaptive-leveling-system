"""Testes unitários para o serviço de extração de pré-requisitos."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from backend.domain.models.pdf import PDFDocument
from backend.domain.models.prerequisite import ConceptNode, KnowledgeGraph, Prerequisite
from backend.services.prerequisite_service import _load_prompt_template, extract_prerequisites


@pytest.fixture
def mock_pdf_doc():
    return PDFDocument(
        id=uuid4(),
        hash="test_hash",
        filename="aula.pdf",
        size=1024,
        bucket_key="uploads/aula.pdf",
        content_text="Texto da aula sobre Limites.",
    )


@pytest.fixture
def mock_knowledge_graph(mock_pdf_doc):
    return KnowledgeGraph(
        pdf_id=str(mock_pdf_doc.id),
        main_concepts=[
            ConceptNode(
                name="Limites", description="Definição de limites", prerequisites=["Álgebra"]
            )
        ],
        prerequisites=[
            Prerequisite(
                name="Álgebra",
                description="Base necessária",
                importance="Critical",
                topics=["Polinômios"],
            )
        ],
    )


@pytest.mark.asyncio
async def test_extract_prerequisites_success(mock_pdf_doc, mock_knowledge_graph):
    """Testa o fluxo de sucesso da extração de pré-requisitos."""
    pdf_id = mock_pdf_doc.id

    with (
        patch(
            "backend.services.prerequisite_service.get_knowledge_graph_by_pdf_id",
            new_callable=AsyncMock,
        ) as mock_get_graph,
        patch(
            "backend.services.prerequisite_service.get_pdf_by_id", new_callable=AsyncMock
        ) as mock_get_pdf,
        patch("backend.services.prerequisite_service.LLMFactory.get_provider") as mock_llm_factory,
        patch(
            "backend.services.prerequisite_service.save_knowledge_graph", new_callable=AsyncMock
        ) as mock_save,
    ):
        # Setup mocks
        mock_get_graph.return_value = None
        mock_get_pdf.return_value = mock_pdf_doc

        mock_llm = AsyncMock()
        mock_llm.generate_structured.return_value = mock_knowledge_graph
        mock_llm.get_provider_name.return_value = "mock"
        mock_llm_factory.return_value = mock_llm

        mock_save.return_value = mock_knowledge_graph

        # Execução
        result = await extract_prerequisites(pdf_id)

        # Asserts
        assert result.pdf_id == str(pdf_id)
        assert len(result.main_concepts) == 1
        assert result.main_concepts[0].name == "Limites"

        mock_llm.generate_structured.assert_called_once()
        mock_save.assert_called_once()


def test_load_prompt_template():
    """Testa que o template do prompt é carregado corretamente."""
    template = _load_prompt_template()
    assert "{{content_text}}" in template
    assert "JSON" in template
