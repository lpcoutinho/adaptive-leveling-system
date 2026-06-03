"""Serviço de gerenciamento de quiz e correção de respostas."""

from uuid import UUID

from backend.domain.models.quiz import QuizAnswer, QuizSession, SessionStatus
from backend.infrastructure.repository.assessment_repository import get_assessment_by_id
from backend.infrastructure.repository.student_repository import save_quiz_session
from backend.infrastructure.student_cache import get_session, save_session
from backend.llm.evaluators.answer_evaluator import AnswerEvaluator


async def start_quiz(assessment_id: UUID, student_id: str = "anonymous") -> QuizSession:
    """Inicia uma nova sessão de quiz."""
    assessment = await get_assessment_by_id(assessment_id)
    if not assessment:
        raise ValueError(f"Avaliação {assessment_id} não encontrada.")
    if not assessment.questions:
        raise ValueError("A avaliação não possui questões.")

    session = QuizSession(
        assessment_id=str(assessment_id),
        student_id=student_id,
        max_score=float(len(assessment.questions) * 100),
    )
    await save_session(session)
    return session


async def get_next_question(session_id: UUID) -> dict | None:
    """Retorna a próxima questão não respondida."""
    session = await get_session(session_id)
    if not session or session.status != SessionStatus.IN_PROGRESS:
        return None

    assessment = await get_assessment_by_id(UUID(session.assessment_id))
    if not assessment:
        return None

    answered_ids = {a.question_id for a in session.answers}
    for q in assessment.questions:
        if str(q.id) not in answered_ids:
            return q.model_dump(mode="json")

    return None


async def submit_answer(
    session_id: UUID,
    question_id: str,
    student_answer: str,
) -> tuple[QuizSession, QuizAnswer | None]:
    """Submete resposta, corrige e retorna sessão atualizada."""
    session = await get_session(session_id)
    if not session or session.status != SessionStatus.IN_PROGRESS:
        raise ValueError("Sessão inválida ou já finalizada.")

    assessment = await get_assessment_by_id(UUID(session.assessment_id))
    if not assessment:
        raise ValueError("Avaliação não encontrada.")

    question = next((q for q in assessment.questions if str(q.id) == question_id), None)
    if not question:
        raise ValueError(f"Questão {question_id} não encontrada.")

    if question.type.value == "multiple_choice":
        result = AnswerEvaluator.evaluate_mcq(student_answer, question.correct_answer)
    else:
        evaluator = AnswerEvaluator()
        result = await evaluator.evaluate(
            question_text=question.text,
            question_type=question.type.value,
            expected_answer=question.correct_answer,
            student_answer=student_answer,
        )

    answer = QuizAnswer(
        question_id=question_id,
        question_type=question.type.value,
        student_answer=student_answer,
        correct_answer=question.correct_answer,
        score=result.score,
        justification=result.justification,
    )

    session.answers.append(answer)
    session.total_score = sum(a.score for a in session.answers)
    await save_session(session)

    return session, answer


async def finish_quiz(session_id: UUID) -> QuizSession:
    """Finaliza o quiz e persiste no PostgreSQL."""
    session = await get_session(session_id)
    if not session:
        raise ValueError("Sessão não encontrada.")

    session.status = SessionStatus.COMPLETED
    session.total_score = sum(a.score for a in session.answers)

    persisted = await save_quiz_session(session)
    return persisted
