"""Schemas Pydantic para API de quiz."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class StartQuizRequest(BaseModel):
    assessment_id: UUID
    student_id: str = "anonymous"


class StartQuizResponse(BaseModel):
    session_id: UUID
    total_questions: int
    max_score: float

    model_config = ConfigDict(from_attributes=True)


class SubmitAnswerRequest(BaseModel):
    question_id: str
    student_answer: str


class AnswerResult(BaseModel):
    question_id: str
    question_type: str
    student_answer: str
    score: float
    justification: str


class SubmitAnswerResponse(BaseModel):
    session_id: UUID
    answer: AnswerResult
    total_score: float
    max_score: float
    questions_remaining: int


class FinishQuizResponse(BaseModel):
    session_id: UUID
    total_score: float
    max_score: float
    percentage: float
    status: str
