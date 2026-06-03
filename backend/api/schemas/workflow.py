from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExecuteWorkflowRequest(BaseModel):
    pdf_id: UUID


class WorkflowResponse(BaseModel):
    workflow_id: UUID
    pdf_id: UUID
    status: str
    current_node: str = ""
    progress: float = 0.0
    error: str | None = None
    created_at: str = ""
    updated_at: str = ""

    model_config = ConfigDict(from_attributes=True)


class WorkflowExecuteResult(BaseModel):
    workflow_id: UUID
    status: str
    progress: float = 0.0
    error: str | None = None
    state: dict | None = None
