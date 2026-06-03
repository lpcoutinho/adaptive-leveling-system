from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GapExplanationSchema(BaseModel):
    gap_name: str
    importance: str
    current_score: float
    why_important: str
    explanation: str
    calculus_example: str
    exercise: str
    exercise_answer: str


class StudyStepSchema(BaseModel):
    order: int
    gap_name: str
    completed: bool = False


class LevelingPlanResponse(BaseModel):
    id: UUID
    readiness_id: UUID
    student_id: str
    explanations: list[GapExplanationSchema]
    study_order: list[StudyStepSchema]
    total_gaps: int
    total_completed: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class GenerateLevelingRequest(BaseModel):
    session_id: UUID
    readiness_id: UUID
