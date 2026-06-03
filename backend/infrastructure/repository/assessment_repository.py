"""Repositório para persistência de avaliações diagnósticas."""

import json
from uuid import UUID

from backend.domain.models.assessment import Assessment, QuizQuestion
from backend.infrastructure.database import execute_query


async def save_assessment(assessment: Assessment) -> Assessment:
    """Salva uma avaliação no banco de dados.

    Usa upsert para garantir idempotência: se já existe para o pdf_id, atualiza.
    """
    query = """
        INSERT INTO assessments (id, pdf_id, questions)
        VALUES ($1, $2, $3)
        ON CONFLICT (pdf_id) DO UPDATE
        SET questions = EXCLUDED.questions,
            updated_at = NOW()
        RETURNING id, created_at, updated_at
    """
    questions_json = json.dumps([q.model_dump(mode="json") for q in assessment.questions])

    result = await execute_query(
        query,
        assessment.id,
        UUID(assessment.pdf_id) if isinstance(assessment.pdf_id, str) else assessment.pdf_id,
        questions_json,
    )

    if result:
        row = result[0]
        assessment.id = row["id"]
        assessment.created_at = row["created_at"]
        assessment.updated_at = row["updated_at"]

    return assessment


async def get_assessment_by_pdf_id(pdf_id: UUID) -> Assessment | None:
    """Busca avaliação associada a um PDF."""
    query = "SELECT * FROM assessments WHERE pdf_id = $1"
    result = await execute_query(query, pdf_id)

    if not result:
        return None

    row = result[0]
    questions_data = row["questions"]
    if isinstance(questions_data, str):
        questions_data = json.loads(questions_data)

    return Assessment(
        id=row["id"],
        pdf_id=str(row["pdf_id"]),
        questions=[QuizQuestion(**q) for q in questions_data],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


async def get_assessment_by_id(assessment_id: UUID) -> Assessment | None:
    """Busca avaliação pelo ID."""
    query = "SELECT * FROM assessments WHERE id = $1"
    result = await execute_query(query, assessment_id)

    if not result:
        return None

    row = result[0]
    questions_data = row["questions"]
    if isinstance(questions_data, str):
        questions_data = json.loads(questions_data)

    return Assessment(
        id=row["id"],
        pdf_id=str(row["pdf_id"]),
        questions=[QuizQuestion(**q) for q in questions_data],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
