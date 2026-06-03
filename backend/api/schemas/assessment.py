"""Schemas Pydantic para validação de dados de API de avaliações."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class QuizQuestionSchema(BaseModel):
    id: UUID
    type: str
    text: str
    options: list[str] = []
    correct_answer: str
    difficulty: float
    topic: str
    justification: str


class AssessmentResponse(BaseModel):
    id: UUID
    pdf_id: UUID
    questions: list[QuizQuestionSchema]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
