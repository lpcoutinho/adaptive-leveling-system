from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, Field

from backend.domain.models.common import TimestampModel, UUIDModel


class ReadinessLevel(StrEnum):
    READY = "ready"
    NEEDS_REVIEW = "needs_review"
    NOT_READY = "not_ready"


class GapAnalysis(BaseModel):
    prerequisite_name: str
    prerequisite_id: str = ""
    score: float = 0.0
    importance: str = "Helpful"
    is_gap: bool = False
    is_strength: bool = False


class ReadinessResult(UUIDModel, TimestampModel):
    session_id: UUID
    pdf_id: UUID
    overall_score: float = 0.0
    level: ReadinessLevel = ReadinessLevel.NEEDS_REVIEW
    gaps: list[GapAnalysis] = Field(default_factory=list)
    strengths: list[GapAnalysis] = Field(default_factory=list)
    total_prerequisites: int = 0
    total_gaps: int = 0
    total_strengths: int = 0
