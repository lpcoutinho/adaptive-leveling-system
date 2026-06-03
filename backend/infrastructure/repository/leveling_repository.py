import json
from uuid import UUID

from backend.domain.models.leveling import GapExplanation, LevelingPlan, StudyStep
from backend.infrastructure.database import execute_query


async def save_leveling_plan(plan: LevelingPlan) -> LevelingPlan:
    query = """
        INSERT INTO leveling_plans
            (id, readiness_id, student_id, explanations, study_order,
             total_gaps, total_completed)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (readiness_id) DO UPDATE
        SET explanations = EXCLUDED.explanations,
            study_order = EXCLUDED.study_order,
            total_gaps = EXCLUDED.total_gaps,
            total_completed = EXCLUDED.total_completed,
            updated_at = NOW()
        RETURNING id, created_at, updated_at
    """
    expl_json = json.dumps([e.model_dump(mode="json") for e in plan.explanations])
    order_json = json.dumps([s.model_dump(mode="json") for s in plan.study_order])

    result = await execute_query(
        query,
        plan.id,
        plan.readiness_id,
        plan.student_id,
        expl_json,
        order_json,
        plan.total_gaps,
        plan.total_completed,
    )
    if result:
        row = result[0]
        plan.id = row["id"]
        plan.created_at = row["created_at"]
        plan.updated_at = row["updated_at"]
    return plan


async def get_leveling_plan(plan_id: UUID) -> LevelingPlan | None:
    query = "SELECT * FROM leveling_plans WHERE id = $1"
    result = await execute_query(query, plan_id)
    if not result:
        return None
    row = result[0]

    expl_data = row["explanations"]
    if isinstance(expl_data, str):
        expl_data = json.loads(expl_data)
    order_data = row["study_order"]
    if isinstance(order_data, str):
        order_data = json.loads(order_data)

    return LevelingPlan(
        id=row["id"],
        readiness_id=row["readiness_id"],
        student_id=row["student_id"],
        explanations=[GapExplanation(**e) for e in expl_data],
        study_order=[StudyStep(**s) for s in order_data],
        total_gaps=row["total_gaps"],
        total_completed=row["total_completed"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


async def get_plan_by_readiness(readiness_id: UUID) -> LevelingPlan | None:
    query = "SELECT * FROM leveling_plans WHERE readiness_id = $1"
    result = await execute_query(query, readiness_id)
    if not result:
        return None
    return await get_leveling_plan(result[0]["id"])
