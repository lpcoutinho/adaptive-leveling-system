from enum import StrEnum

from pydantic import BaseModel


class WorkflowStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    AWAITING_INPUT = "awaiting_input"
    COMPLETED = "completed"
    FAILED = "failed"


class GraphState(BaseModel):
    pdf_id: str | None = None
    session_id: str | None = None
    readiness_id: str | None = None
    knowledge_graph: dict | None = None
    assessment: dict | None = None
    quiz_session: dict | None = None
    readiness_result: dict | None = None
    leveling_plan: dict | None = None
    status: WorkflowStatus = WorkflowStatus.PENDING
    error: str | None = None
    current_node: str = ""
    progress: float = 0.0
    created_at: str = ""
    updated_at: str = ""
