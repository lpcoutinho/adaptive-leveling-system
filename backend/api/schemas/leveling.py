"""Schemas da API para o módulo de nivelamento (leveling)."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GapExplanationSchema(BaseModel):
    """Schema de resposta para explicação de um gap de conhecimento."""

    gap_name: str = Field(..., description="Nome do conceito com gap")
    importance: str = Field(..., description="Critical, Important ou Helpful")
    current_score: float = Field(..., description="Score atual do aluno no tópico (0-100)")
    why_important: str = Field(..., description="Por que este conceito é fundamental")
    explanation: str = Field(..., description="Explicação didática do conceito")
    discipline_example: str = Field(..., description="Exemplo prático aplicado à disciplina")
    exercise: str = Field(..., description="Exercício para o aluno praticar")
    exercise_answer: str = Field(..., description="Resolução passo a passo do exercício")


class StudyStepSchema(BaseModel):
    """Schema de resposta para uma etapa do plano de estudos."""

    order: int = Field(..., description="Ordem de estudo recomendada")
    gap_name: str = Field(..., description="Nome do gap a ser estudado")
    completed: bool = Field(default=False, description="Se o aluno já concluiu esta etapa")


class LevelingPlanResponse(BaseModel):
    """Schema de resposta completa do plano de nivelamento."""

    id: UUID = Field(..., description="ID único do plano")
    readiness_id: UUID = Field(..., description="ID do resultado de prontidão associado")
    student_id: str = Field(..., description="Identificador do aluno")
    explanations: list[GapExplanationSchema] = Field(..., description="Explicações dos gaps")
    study_order: list[StudyStepSchema] = Field(..., description="Ordem de estudo recomendada")
    total_gaps: int = Field(..., description="Total de gaps identificados")
    total_completed: int = Field(..., description="Total de etapas concluídas")
    created_at: datetime = Field(..., description="Data de criação")
    updated_at: datetime = Field(..., description="Data da última atualização")

    model_config = ConfigDict(from_attributes=True)


class GenerateLevelingRequest(BaseModel):
    """Schema de requisição para geração de plano de nivelamento."""

    session_id: UUID = Field(..., description="ID da sessão do quiz")
    readiness_id: UUID = Field(..., description="ID do resultado de prontidão")
    force_regenerate: bool = Field(
        default=False, description="Força regeneração mesmo se plano existir"
    )
