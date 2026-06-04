"""Rotas da API para orquestração do workflow de nivelamento adaptativo."""

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
    resume_workflow,
)

router = APIRouter(prefix="/workflow", tags=["Workflow"])


@router.post("/execute", response_model=WorkflowExecuteResult, status_code=201)
async def trigger_workflow(request: ExecuteWorkflowRequest):
    """
    Dispara um novo workflow de nivelamento para um PDF.

    Responsável por orquestrar extração de pré-requisitos, geração de
    avaliação, quiz, detecção de gaps e conteúdo de nivelamento.
    """
    try:
        result = await execute_workflow(request.pdf_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no workflow: {str(e)}") from e


@router.get("/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_status(workflow_id: UUID):
    """Retorna o estado atual de um workflow pelo seu ID."""
    result = await get_workflow(workflow_id)
    if not result:
        raise HTTPException(status_code=404, detail="Workflow não encontrado.")
    return result


@router.post("/{workflow_id}/resume", response_model=WorkflowExecuteResult)
async def resume_workflow_execution(workflow_id: UUID):
    """
    Retoma um workflow que estava aguardando input do usuário.

    Útil para continuar a execução após o aluno finalizar o quiz.
    """
    try:
        result = await resume_workflow(workflow_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao retomar workflow: {str(e)}") from e


@router.delete("/{workflow_id}", status_code=204)
async def delete_workflow(workflow_id: UUID):
    """Cancela e remove um workflow em execução."""
    cancelled = await cancel_workflow(workflow_id)
    if not cancelled:
        raise HTTPException(status_code=404, detail="Workflow não encontrado.")
