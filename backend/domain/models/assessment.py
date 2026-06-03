from enum import StrEnum

from pydantic import Field

from backend.domain.models.common import TimestampModel, UUIDModel


class QuestionType(StrEnum):
    MULTIPLE_CHOICE = "multiple_choice"
    SHORT_ANSWER = "short_answer"
    CALCULATION = "calculation"


class QuizQuestion(UUIDModel):
    type: QuestionType
    text: str = Field(..., description="Enunciado da questão")
    options: list[str] = Field(default_factory=list, description="Alternativas (apenas MC)")
    correct_answer: str = Field(..., description="Resposta correta")
    difficulty: float = Field(default=0.5, ge=0.0, le=1.0, description="Dificuldade 0.0-1.0")
    topic: str = Field(..., description="Pré-requisito ao qual a questão pertence")
    justification: str = Field(..., description="Explicação da resposta correta")


class Assessment(UUIDModel, TimestampModel):
    pdf_id: str = Field(default="", description="Referência ao PDF original")
    questions: list[QuizQuestion] = Field(default_factory=list)
