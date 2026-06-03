from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from backend.domain.models.common import TimestampModel, UUIDModel


class SessionStatus(StrEnum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    TIMEOUT = "timeout"


class QuizAnswer(BaseModel):
    question_id: str
    question_type: str
    student_answer: str
    correct_answer: str = ""
    score: float = 0.0
    justification: str = ""
    answered_at: datetime = Field(default_factory=datetime.now)


class QuizSession(UUIDModel, TimestampModel):
    assessment_id: str = Field(default="", description="ID da avaliação")
    student_id: str = Field(default="anonymous", description="ID do estudante")
    status: SessionStatus = SessionStatus.IN_PROGRESS
    answers: list[QuizAnswer] = Field(default_factory=list)
    total_score: float = 0.0
    max_score: float = 0.0
