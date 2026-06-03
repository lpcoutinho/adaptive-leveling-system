from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GapAnalysisSchema(BaseModel):
    prerequisite_name: str
    prerequisite_id: str = ""
    score: float
    importance: str
    is_gap: bool
    is_strength: bool


class ReadinessResponse(BaseModel):
    id: UUID
    session_id: UUID
    pdf_id: UUID
    overall_score: float
    level: str
    gaps: list[GapAnalysisSchema]
    strengths: list[GapAnalysisSchema]
    total_prerequisites: int
    total_gaps: int
    total_strengths: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AnalyzeRequest(BaseModel):
    session_id: UUID
    pdf_id: UUID
