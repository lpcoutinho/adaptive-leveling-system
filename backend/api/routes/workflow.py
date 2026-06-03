from uuid import UUID

from fastapi import APIRouter, HTTPException

from backend.api.schemas.workflow import (
    ExecuteWorkflowRequest,
    WorkflowExecuteResult,
    WorkflowResponse,
)
from backend.services.workflow_service import (
    cancel_workflow,
    execute_workflow,
    get_workflow,
)

router = APIRouter(prefix="/workflow", tags=["Workflow"])


@router.post("/execute", response_model=WorkflowExecuteResult, status_code=201)
async def trigger_workflow(request: ExecuteWorkflowRequest):
    try:
        result = await execute_workflow(request.pdf_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no workflow: {str(e)}") from e


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_status(workflow_id: UUID):
    result = await get_workflow(workflow_id)
    if not result:
        raise HTTPException(status_code=404, detail="Workflow não encontrado.")
    return result


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: UUID):
    cancelled = await cancel_workflow(workflow_id)
    if not cancelled:
        raise HTTPException(status_code=404, detail="Workflow não encontrado.")
