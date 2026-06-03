import json
from uuid import UUID

from backend.domain.models.readiness import GapAnalysis, ReadinessResult
from backend.infrastructure.database import execute_query


async def save_readiness_result(result: ReadinessResult) -> ReadinessResult:
    query = """
        INSERT INTO readiness_results
            (id, session_id, pdf_id, overall_score, level, gaps, strengths,
             total_prerequisites, total_gaps, total_strengths)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
        ON CONFLICT (session_id) DO UPDATE
        SET overall_score = EXCLUDED.overall_score,
            level = EXCLUDED.level,
            gaps = EXCLUDED.gaps,
            strengths = EXCLUDED.strengths,
            total_prerequisites = EXCLUDED.total_prerequisites,
            total_gaps = EXCLUDED.total_gaps,
            total_strengths = EXCLUDED.total_strengths,
            updated_at = NOW()
        RETURNING id, created_at, updated_at
    """
    gaps_json = json.dumps([g.model_dump(mode="json") for g in result.gaps])
    strengths_json = json.dumps([s.model_dump(mode="json") for s in result.strengths])

    params = await execute_query(
        query,
        result.id,
        result.session_id,
        result.pdf_id,
        result.overall_score,
        result.level.value,
        gaps_json,
        strengths_json,
        result.total_prerequisites,
        result.total_gaps,
        result.total_strengths,
    )
    if params:
        row = params[0]
        result.id = row["id"]
        result.created_at = row["created_at"]
        result.updated_at = row["updated_at"]
    return result


async def get_readiness_by_id(result_id: UUID) -> ReadinessResult | None:
    query = "SELECT * FROM readiness_results WHERE id = $1"
    result = await execute_query(query, result_id)
    if not result:
        return None
    return _row_to_result(result[0])


def _row_to_result(row: dict) -> ReadinessResult:
    gaps_data = row["gaps"]
    if isinstance(gaps_data, str):
        gaps_data = json.loads(gaps_data)
    strengths_data = row["strengths"]
    if isinstance(strengths_data, str):
        strengths_data = json.loads(strengths_data)
    return ReadinessResult(
        id=row["id"],
        session_id=row["session_id"],
        pdf_id=row["pdf_id"],
        overall_score=row["overall_score"],
        level=row["level"],
        gaps=[GapAnalysis(**g) for g in gaps_data],
        strengths=[GapAnalysis(**s) for s in strengths_data],
        total_prerequisites=row["total_prerequisites"],
        total_gaps=row["total_gaps"],
        total_strengths=row["total_strengths"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


async def get_readiness_by_session(session_id: UUID) -> ReadinessResult | None:
    query = "SELECT * FROM readiness_results WHERE session_id = $1"
    result = await execute_query(query, session_id)
    if not result:
        return None

    return _row_to_result(result[0])
