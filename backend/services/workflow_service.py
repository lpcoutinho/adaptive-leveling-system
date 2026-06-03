from uuid import UUID

from backend.infrastructure.repository.workflow_repository import (
    get_workflow_state,
    save_workflow_state,
)
from backend.workflows.readiness_graph import app as graph_app
from backend.workflows.states import WorkflowStatus


async def execute_workflow(pdf_id: UUID) -> dict:
    import uuid

    workflow_id = uuid.uuid4()
    initial_state = {
        "pdf_id": str(pdf_id),
        "status": WorkflowStatus.IN_PROGRESS.value,
        "progress": 0.0,
        "current_node": "extract",
        "created_at": "",
        "updated_at": "",
    }

    await save_workflow_state(
        workflow_id=workflow_id,
        pdf_id=pdf_id,
        status=WorkflowStatus.IN_PROGRESS.value,
        current_node="extract",
        state=initial_state,
        progress=0.0,
    )

    try:
        final_state = await graph_app.ainvoke(initial_state)
        status = final_state.get("status", WorkflowStatus.COMPLETED.value)
        progress = final_state.get("progress", 1.0)
        err = final_state.get("error")

        await save_workflow_state(
            workflow_id=workflow_id,
            pdf_id=pdf_id,
            status=status,
            current_node=final_state.get("current_node", ""),
            state=final_state,
            progress=progress,
            error=err,
        )

        return {
            "workflow_id": str(workflow_id),
            "status": status,
            "progress": progress,
            "state": final_state,
        }
    except Exception as e:
        await save_workflow_state(
            workflow_id=workflow_id,
            pdf_id=pdf_id,
            status=WorkflowStatus.FAILED.value,
            current_node="",
            state=initial_state,
            progress=0.0,
            error=str(e),
        )
        return {
            "workflow_id": str(workflow_id),
            "status": WorkflowStatus.FAILED.value,
            "progress": 0.0,
            "error": str(e),
            "state": initial_state,
        }


async def get_workflow(workflow_id: UUID) -> dict | None:
    return await get_workflow_state(workflow_id)


async def cancel_workflow(workflow_id: UUID) -> bool:
    from backend.infrastructure.database import execute_query

    result = await execute_query(
        "UPDATE workflow_executions SET status = $1, updated_at = NOW() WHERE id = $2 RETURNING id",
        WorkflowStatus.FAILED.value,
        workflow_id,
    )
    return bool(result)
