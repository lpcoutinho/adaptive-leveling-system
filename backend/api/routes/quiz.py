"""Endpoints da API para quiz interativo."""

from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.api.schemas.quiz import (
    AnswerResult,
    BatchAnswerRequest,
    BatchAnswerResponse,
    BatchEvalItem,
    FinishQuizResponse,
    StartQuizRequest,
    StartQuizResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
)
from backend.infrastructure.repository.assessment_repository import get_assessment_by_id
from backend.services.quiz_service import (
    evaluate_pending_answers,
    finish_quiz,
    get_next_question,
    start_quiz,
    submit_answer,
)

router = APIRouter(prefix="/quiz", tags=["Quiz"])


@router.post("/start", response_model=StartQuizResponse, status_code=201)
async def api_start_quiz(req: StartQuizRequest):
    """Inicia uma nova sessão de quiz."""
    try:
        session = await start_quiz(req.assessment_id, req.student_id)
        assessment = await get_assessment_by_id(req.assessment_id)
        qty = len(assessment.questions) if assessment else 0
        return StartQuizResponse(
            session_id=session.id,
            total_questions=qty,
            max_score=session.max_score,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@router.get("/{session_id}/next")
async def api_next_question(session_id: UUID):
    """Retorna a próxima questão não respondida."""
    question = await get_next_question(session_id)
    if not question:
        raise HTTPException(status_code=404, detail="Nenhuma questão pendente ou sessão inválida.")
    return question


@router.post("/{session_id}/answer", response_model=SubmitAnswerResponse)
async def api_submit_answer(session_id: UUID, req: SubmitAnswerRequest):
    """Submete resposta e retorna correção."""
    try:
        session, answer = await submit_answer(session_id, req.question_id, req.student_answer)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    if not answer:
        raise HTTPException(status_code=500, detail="Erro ao processar resposta.")

    answered = len(session.answers)
    total = int(session.max_score / 100)
    remaining = max(0, total - answered)

    return SubmitAnswerResponse(
        session_id=session.id,
        answer=AnswerResult(
            question_id=answer.question_id,
            question_type=answer.question_type,
            student_answer=answer.student_answer,
            score=answer.score,
            justification=answer.justification,
        ),
        total_score=session.total_score,
        max_score=session.max_score,
        questions_remaining=remaining,
    )


@router.post("/{session_id}/evaluate-pending", response_model=BatchAnswerResponse)
async def api_evaluate_pending(session_id: UUID, req: BatchAnswerRequest):
    """Avalia respostas SA/Calc pendentes em lote num único prompt LLM."""
    pending = [(a.question_id, a.student_answer) for a in req.answers]
    try:
        results = await evaluate_pending_answers(session_id, pending)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    items = [
        BatchEvalItem(
            question_id=qid,
            score=r["score"],
            justification=r["justification"],
        )
        for qid, r in results.items()
    ]
    return BatchAnswerResponse(session_id=str(session_id), results=items)


@router.post("/{session_id}/finish", response_model=FinishQuizResponse)
async def api_finish_quiz(session_id: UUID):
    """Finaliza o quiz e persiste resultados."""
    try:
        session = await finish_quiz(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e

    pct = (session.total_score / session.max_score * 100) if session.max_score > 0 else 0
    return FinishQuizResponse(
        session_id=session.id,
        total_score=session.total_score,
        max_score=session.max_score,
        percentage=round(pct, 1),
        status=session.status.value,
    )
