"""Repositório para persistência de sessões de quiz no PostgreSQL."""

import json
from uuid import UUID

from backend.domain.models.quiz import QuizAnswer, QuizSession
from backend.infrastructure.database import execute_query


async def save_quiz_session(session: QuizSession) -> QuizSession:
    """Salva/finaliza sessão de quiz no PostgreSQL."""
    query = """
        INSERT INTO quiz_sessions
            (id, assessment_id, student_id, status, answers, total_score, max_score)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (id) DO UPDATE
        SET status = EXCLUDED.status,
            answers = EXCLUDED.answers,
            total_score = EXCLUDED.total_score,
            max_score = EXCLUDED.max_score,
            updated_at = NOW()
        RETURNING id, created_at, updated_at
    """
    answers_json = json.dumps([a.model_dump(mode="json") for a in session.answers])
    result = await execute_query(
        query,
        session.id,
        (
            UUID(session.assessment_id)
            if isinstance(session.assessment_id, str)
            else session.assessment_id
        ),
        session.student_id,
        session.status.value,
        answers_json,
        session.total_score,
        session.max_score,
    )
    if result:
        row = result[0]
        session.id = row["id"]
        session.created_at = row["created_at"]
        session.updated_at = row["updated_at"]
    return session


async def get_quiz_session(session_id: UUID) -> QuizSession | None:
    """Busca sessão persistida."""
    query = "SELECT * FROM quiz_sessions WHERE id = $1"
    result = await execute_query(query, session_id)
    if not result:
        return None
    row = result[0]
    answers_data = row["answers"]
    if isinstance(answers_data, str):
        answers_data = json.loads(answers_data)
    return QuizSession(
        id=row["id"],
        assessment_id=str(row["assessment_id"]),
        student_id=row["student_id"],
        status=row["status"],
        answers=[QuizAnswer(**a) for a in answers_data],
        total_score=row["total_score"],
        max_score=row["max_score"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
