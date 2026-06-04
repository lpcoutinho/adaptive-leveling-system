"""Schemas da API para o módulo de workflow."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ExecuteWorkflowRequest(BaseModel):
    """Requisição para iniciar um novo workflow de nivelamento."""

    pdf_id: UUID = Field(..., description="ID do PDF processado para iniciar o workflow")


class WorkflowResponse(BaseModel):
    """Resposta com o estado atual de um workflow."""

    workflow_id: UUID = Field(..., alias="id", description="ID único do workflow")
    pdf_id: UUID = Field(..., description="ID do PDF associado")
    status: str = Field(..., description="Status atual (in_progress, completed, failed, etc.)")
    current_node: str = Field(default="", description="Nó atual no grafo de execução")
    progress: float = Field(default=0.0, description="Progresso de 0.0 a 1.0")
    error: str | None = Field(default=None, description="Mensagem de erro, se houver")
    created_at: str = Field(default="", description="Data de criação")
    updated_at: str = Field(default="", description="Data da última atualização")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class WorkflowExecuteResult(BaseModel):
    """Resposta após executar ou retomar um workflow."""

    workflow_id: UUID = Field(..., description="ID único do workflow criado/retomado")
    status: str = Field(..., description="Status após a execução")
    progress: float = Field(default=0.0, description="Progresso de 0.0 a 1.0")
    error: str | None = Field(default=None, description="Mensagem de erro, se houver")
    state: dict | None = Field(default=None, description="Estado completo do workflow")
