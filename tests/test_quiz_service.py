"""Testes para o serviço de quiz."""

from unittest.mock import AsyncMock, patch
from uuid import UUID, uuid4

import pytest

from backend.domain.models.assessment import Assessment, QuestionType, QuizQuestion
from backend.domain.models.quiz import QuizAnswer, QuizSession, SessionStatus
from backend.services.quiz_service import finish_quiz, start_quiz, submit_answer

pytestmark = pytest.mark.usefixtures("clean_database")


@pytest.fixture
def mock_assessment_id() -> UUID:
    return uuid4()


@pytest.fixture
def mock_assessment(mock_assessment_id: UUID) -> Assessment:
    return Assessment(
        id=mock_assessment_id,
        pdf_id=str(uuid4()),
        questions=[
            QuizQuestion(
                type=QuestionType.MULTIPLE_CHOICE,
                text="Qual é a derivada de x²?",
                options=["a) 2x", "b) x²", "c) 2", "d) 0"],
                correct_answer="2x",
                difficulty=0.3,
                topic="Derivadas",
                justification="Regra da potência.",
            ),
            QuizQuestion(
                type=QuestionType.SHORT_ANSWER,
                text="Defina limite.",
                correct_answer="Valor que a função se aproxima.",
                difficulty=0.5,
                topic="Limites",
                justification="Conceito fundamental.",
            ),
        ],
    )


@pytest.mark.asyncio
async def test_start_quiz_success(mock_assessment_id, mock_assessment):
    """Testa criação de sessão de quiz."""
    with (
        patch(
            "backend.services.quiz_service.get_assessment_by_id",
            new_callable=AsyncMock,
        ) as mock_get,
        patch(
            "backend.services.quiz_service.save_session",
            new_callable=AsyncMock,
        ) as mock_save,
    ):
        mock_get.return_value = mock_assessment
        mock_save.return_value = True

        session = await start_quiz(mock_assessment_id, "test_student")

        assert session.status == SessionStatus.IN_PROGRESS
        assert session.student_id == "test_student"
        assert session.max_score == 200.0
        mock_save.assert_called_once()


@pytest.mark.asyncio
async def test_start_quiz_no_questions(mock_assessment_id):
    """Testa erro ao iniciar quiz sem questões."""
    with patch(
        "backend.services.quiz_service.get_assessment_by_id",
        new_callable=AsyncMock,
    ) as mock_get:
        empty = Assessment(pdf_id=str(uuid4()), questions=[])
        mock_get.return_value = empty

        with pytest.raises(ValueError, match="não possui questões"):
            await start_quiz(mock_assessment_id)


@pytest.mark.asyncio
async def test_submit_mcq_answer(mock_assessment_id, mock_assessment):
    """Testa submissão de resposta de múltipla escolha."""
    with (
        patch(
            "backend.services.quiz_service.get_assessment_by_id",
            new_callable=AsyncMock,
        ) as mock_get,
        patch(
            "backend.services.quiz_service.get_session",
            new_callable=AsyncMock,
        ) as mock_sesh,
        patch(
            "backend.services.quiz_service.save_session",
            new_callable=AsyncMock,
        ) as mock_save,
    ):
        session = QuizSession(assessment_id=str(mock_assessment_id), max_score=200.0)
        mock_sesh.return_value = session
        mock_get.return_value = mock_assessment
        mock_save.return_value = True

        updated, answer = await submit_answer(
            session.id, str(mock_assessment.questions[0].id), "2x"
        )

        assert answer is not None
        assert answer.score == 100.0
        assert len(updated.answers) == 1
        mock_save.assert_called_once()


@pytest.mark.asyncio
async def test_finish_quiz(mock_assessment_id):
    """Testa finalização de quiz."""
    with (
        patch(
            "backend.services.quiz_service.get_session",
            new_callable=AsyncMock,
        ) as mock_sesh,
        patch(
            "backend.services.quiz_service.save_quiz_session",
            new_callable=AsyncMock,
        ) as mock_persist,
    ):
        session = QuizSession(
            assessment_id=str(mock_assessment_id),
            max_score=100.0,
            answers=[
                QuizAnswer(question_id="q1", question_type="mc", student_answer="2x", score=100.0),
            ],
        )
        mock_sesh.return_value = session
        mock_persist.return_value = session

        result = await finish_quiz(session.id)

        assert result.status == SessionStatus.COMPLETED
        assert result.total_score == 100.0
        mock_persist.assert_called_once()
