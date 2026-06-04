"""Serviço de orquestração do workflow de nivelamento adaptativo.

Responsável por gerenciar o ciclo de vida dos workflows: criar,
executar, retomar e cancelar. Utiliza o grafo LangGraph para
orquestrar as etapas (extração → avaliação → quiz → gaps → nivelamento).
"""

from uuid import UUID

from backend.infrastructure.repository.workflow_repository import (
    get_workflow_state,
    save_workflow_state,
)
from backend.workflows.readiness_graph import app as graph_app
from backend.workflows.states import WorkflowStatus


async def execute_workflow(pdf_id: UUID) -> dict:
    """
    Inicia e executa um novo workflow de nivelamento para um PDF.

    Fluxo:
    1. Gera um ID único para o workflow
    2. Salva o estado inicial no banco
    3. Invoca o grafo LangGraph (execução assíncrona completa)
    4. Salva o estado final e retorna o resultado

    Args:
        pdf_id: ID do PDF processado.

    Returns:
        Dict com workflow_id, status, progress e state.
    """
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
        # Invoca o grafo LangGraph com o estado inicial
        final_state = await graph_app.ainvoke(initial_state)  # type: ignore[attr-defined]
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
        # Em caso de falha, salva estado de erro e retorna diagnóstico
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


async def resume_workflow(workflow_id: UUID) -> dict:
    """
    Retoma um workflow pausado a partir do seu estado salvo.

    Útil quando o workflow parou em "awaiting_input" (ex: aguardando
    o aluno finalizar o quiz). Recarrega o estado e re-invoca o grafo.

    Args:
        workflow_id: ID do workflow a ser retomado.

    Returns:
        Dict com workflow_id, status, progress e state.

    Raises:
        ValueError: Se o workflow não for encontrado.
    """
    current_data = await get_workflow_state(workflow_id)
    if not current_data:
        raise ValueError("Workflow não encontrado.")

    state = current_data.get("state", {})
    pdf_id = UUID(str(current_data["pdf_id"]))

    try:
        # Re-invoca o grafo com o estado atual (nós idempotentes ignoram etapas já feitas)
        final_state = await graph_app.ainvoke(state)  # type: ignore[attr-defined]

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
            current_node=str(state.get("current_node", "")),  # type: ignore[attr-defined]
            state=state,  # type: ignore[arg-type]
            progress=float(state.get("progress", 0.0)),  # type: ignore[attr-defined]
            error=str(e),
        )
        return {
            "workflow_id": str(workflow_id),
            "status": WorkflowStatus.FAILED.value,
            "progress": float(state.get("progress", 0.0)),  # type: ignore[attr-defined]
            "error": str(e),
            "state": state,
        }


async def get_workflow(workflow_id: UUID) -> dict | None:
    """Retorna o estado atual de um workflow pelo ID."""
    return await get_workflow_state(workflow_id)


async def cancel_workflow(workflow_id: UUID) -> bool:
    """Cancela um workflow em execução, marcando-o como failed no banco."""
    from backend.infrastructure.database import execute_query

    result = await execute_query(
        "UPDATE workflow_executions SET status = $1, updated_at = NOW() WHERE id = $2 RETURNING id",
        WorkflowStatus.FAILED.value,
        workflow_id,
    )
    return bool(result)
