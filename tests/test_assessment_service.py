"""Testes unitários para o serviço de geração de avaliações."""

from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest

from backend.domain.models.assessment import Assessment, QuestionType, QuizQuestion
from backend.llm.prompt_router import PromptRouter, PromptUseCase
from backend.services.assessment_service import generate_assessment

pytestmark = pytest.mark.usefixtures("clean_database")


@pytest.fixture
def mock_pdf_id() -> UUID:
    return uuid4()


@pytest.fixture
def mock_assessment(mock_pdf_id: UUID) -> Assessment:
    return Assessment(
        pdf_id=str(mock_pdf_id),
        questions=[
            QuizQuestion(
                type=QuestionType.MULTIPLE_CHOICE,
                text="Qual é a derivada de x²?",
                options=["a) 2x", "b) x²", "c) 2", "d) 0"],
                correct_answer="2x",
                difficulty=0.3,
                topic="Derivadas",
                justification="Regra da potência: d/dx(x^n) = n·x^(n-1)",
            ),
            QuizQuestion(
                type=QuestionType.SHORT_ANSWER,
                text="Defina o conceito de limite.",
                correct_answer="Valor que a função se aproxima.",
                difficulty=0.5,
                topic="Limites",
                justification="Limite é o conceito fundamental do Cálculo.",
            ),
            QuizQuestion(
                type=QuestionType.CALCULATION,
                text="Calcule ∫₀¹ x² dx",
                correct_answer="1/3",
                difficulty=0.8,
                topic="Integrais",
                justification="∫x² dx = x³/3, avaliada de 0 a 1.",
            ),
        ],
    )


@pytest.fixture
def mock_prerequisites():
    return [
        type(
            "MockPrereq",
            (),
            {
                "name": "Derivadas",
                "description": "Base necessária",
                "importance": "Critical",
                "topics": ["Regra da Cadeia"],
                "model_dump": lambda _self: {"name": "Derivadas", "description": "Base necessária"},
            },
        )()
    ]


@pytest.mark.asyncio
async def test_generate_assessment_success(mock_pdf_id, mock_assessment, mock_prerequisites):
    """Testa o fluxo de sucesso da geração de avaliação."""
    with (
        patch(
            "backend.services.assessment_service.get_assessment_by_pdf_id",
            new_callable=AsyncMock,
        ) as mock_get,
        patch(
            "backend.services.assessment_service.get_knowledge_graph_by_pdf_id",
            new_callable=AsyncMock,
        ) as mock_graph,
        patch("backend.services.assessment_service.LLMFactory.get_provider") as mock_llm_factory,
        patch(
            "backend.services.assessment_service.save_assessment", new_callable=AsyncMock
        ) as mock_save,
    ):
        mock_get.return_value = None
        mock_graph.return_value = type("MockGraph", (), {"prerequisites": mock_prerequisites})()

        mock_llm = AsyncMock()
        mock_llm.generate_structured.return_value = mock_assessment
        mock_llm_factory.return_value = mock_llm

        mock_save.return_value = mock_assessment

        result = await generate_assessment(mock_pdf_id)

        assert len(result.questions) == 3
        assert result.pdf_id == str(mock_pdf_id)
        mock_llm.generate_structured.assert_called_once()
        mock_save.assert_called_once()


@pytest.mark.asyncio
async def test_generate_assessment_no_prerequisites(mock_pdf_id):
    """Testa erro quando não há pré-requisitos extraídos."""
    with (
        patch(
            "backend.services.assessment_service.get_assessment_by_pdf_id",
            new_callable=AsyncMock,
        ) as mock_get,
        patch(
            "backend.services.assessment_service.get_knowledge_graph_by_pdf_id",
            new_callable=AsyncMock,
        ) as mock_graph,
    ):
        mock_get.return_value = None
        mock_graph.return_value = None

        with pytest.raises(ValueError, match="Nenhum pré-requisito encontrado"):
            await generate_assessment(mock_pdf_id)


@pytest.mark.asyncio
async def test_generate_assessment_idempotency(mock_pdf_id, mock_assessment):
    """Testa idempotência: retorna avaliação existente sem gerar novamente."""
    with (
        patch(
            "backend.services.assessment_service.get_assessment_by_pdf_id",
            new_callable=AsyncMock,
        ) as mock_get,
        patch(
            "backend.services.assessment_service.get_knowledge_graph_by_pdf_id",
        ) as mock_graph,
    ):
        mock_get.return_value = mock_assessment

        result = await generate_assessment(mock_pdf_id)

        assert result == mock_assessment
        assert result.pdf_id == str(mock_pdf_id)
        mock_graph.assert_not_called()


def test_prompt_router_carregar_assessment_prompt():
    """Testa que o PromptRouter carrega o prompt de avaliação corretamente."""
    router = PromptRouter()
    template = router.get_prompt(PromptUseCase.ASSESSMENT_GENERATOR)
    assert "{{prerequisites_json}}" in template
    assert "multiple_choice" in template
