from uuid import UUID

from pydantic import BaseModel, Field

from backend.domain.models.common import TimestampModel, UUIDModel


class GapExplanation(BaseModel):
    gap_name: str
    importance: str = "Helpful"
    current_score: float = 0.0
    why_important: str = ""
    explanation: str = ""
    calculus_example: str = ""
    exercise: str = ""
    exercise_answer: str = ""


class StudyStep(BaseModel):
    order: int = 0
    gap_name: str
    explanation_id: str = ""
    completed: bool = False


class LevelingPlan(UUIDModel, TimestampModel):
    readiness_id: UUID
    student_id: str = "anonymous"
    explanations: list[GapExplanation] = Field(default_factory=list)
    study_order: list[StudyStep] = Field(default_factory=list)
    total_gaps: int = 0
    total_completed: int = 0
