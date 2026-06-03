import json
from uuid import UUID

from backend.infrastructure.database import execute_query


async def save_workflow_state(
    workflow_id: UUID,
    pdf_id: UUID,
    status: str,
    current_node: str,
    state: dict,
    progress: float,
    error: str | None = None,
) -> dict | None:
    query = """
        INSERT INTO workflow_executions
            (id, pdf_id, status, current_node, state, progress, error)
        VALUES ($1, $2, $3, $4, $5, $6, $7)
        ON CONFLICT (id) DO UPDATE
        SET status = EXCLUDED.status,
            current_node = EXCLUDED.current_node,
            state = EXCLUDED.state,
            progress = EXCLUDED.progress,
            error = EXCLUDED.error,
            updated_at = NOW()
        RETURNING id, created_at, updated_at
    """
    state_json = json.dumps(state, default=str)
    return await execute_query(  # type: ignore[return-value]
        query,
        workflow_id,
        pdf_id,
        status,
        current_node,
        state_json,
        progress,
        error,
    )


async def get_workflow_state(workflow_id: UUID) -> dict[str, object] | None:
    query = "SELECT * FROM workflow_executions WHERE id = $1"
    result = await execute_query(query, workflow_id)
    if not result:
        return None
    row = result[0]
    state_data = row["state"]
    if isinstance(state_data, str):
        state_data = json.loads(state_data)
    return {
        "id": str(row["id"]),
        "pdf_id": str(row["pdf_id"]),
        "status": row["status"],
        "current_node": row["current_node"],
        "state": state_data,
        "progress": row["progress"],
        "error": row["error"],
        "created_at": row["created_at"].isoformat()
        if hasattr(row["created_at"], "isoformat")
        else str(row["created_at"]),
        "updated_at": row["updated_at"].isoformat()
        if hasattr(row["updated_at"], "isoformat")
        else str(row["updated_at"]),
    }
