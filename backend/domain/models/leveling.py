from uuid import UUID

from pydantic import Field

from backend.domain.models.common import TimestampModel, UUIDModel


class GapExplanation(UUIDModel):
    gap_name: str = Field(..., description="Nome do pré-requisito deficitário")
    importance: str = Field(default="Helpful", description="Critical, Important ou Helpful")
    current_score: float = Field(default=0.0, description="Score atual do aluno (0-100)")
    why_important: str = Field(
        default="", description="Por que o conceito é fundamental na disciplina"
    )
    explanation: str = Field(default="", description="Explicação didática e acessível do conceito")
    discipline_example: str = Field(
        default="", description="Exemplo concreto aplicado à disciplina"
    )
    exercise: str = Field(default="", description="Exercício prático para o aluno")
    exercise_answer: str = Field(default="", description="Resolução passo a passo do exercício")


class StudyStep(UUIDModel):
    order: int = Field(..., description="Ordem da etapa no plano")
    gap_name: str = Field(..., description="Nome do gap correspondente")
    completed: bool = Field(default=False, description="Status de conclusão")


class LevelingPlan(UUIDModel, TimestampModel):
    readiness_id: UUID = Field(..., description="ID do resultado de prontidão que gerou o plano")
    student_id: str = Field(default="anonymous", description="Identificador do aluno")
    explanations: list[GapExplanation] = Field(
        default_factory=list, description="Lista de explicações dos gaps"
    )
    study_order: list[StudyStep] = Field(
        default_factory=list, description="Etapas ordenadas de estudo"
    )
    total_gaps: int = Field(default=0, description="Total de gaps no plano")
    total_completed: int = Field(default=0, description="Total de etapas concluídas")
