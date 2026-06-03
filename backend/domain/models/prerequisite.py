"""Modelos de domínio para pré-requisitos e grafos de conhecimento."""

from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from backend.domain.models.common import TimestampModel, UUIDModel


class Prerequisite(BaseModel):
    """Representa um conhecimento prévio necessário para entender a aula."""

    name: str = Field(..., description="Nome do conceito pré-requisito")
    description: str = Field(
        ..., description="Breve explicação do porquê este conceito é necessário"
    )
    importance: Literal["Critical", "Important", "Helpful"] = Field(
        ..., description="Nível de importância para o entendimento da aula"
    )
    topics: list[str] = Field(
        default_factory=list, description="Tópicos específicos dentro do pré-requisito"
    )


class ConceptNode(BaseModel):
    """Representa um conceito principal abordado na aula e seus pré-requisitos."""

    name: str = Field(..., description="Nome do conceito da aula")
    description: str = Field(..., description="Breve resumo do que o conceito aborda")
    prerequisites: list[str] = Field(
        default_factory=list,
        description="Lista de nomes de pré-requisitos necessários para este conceito",
    )


class KnowledgeGraph(UUIDModel, TimestampModel):
    """Estrutura completa que mapeia a aula, seus conceitos e pré-requisitos."""

    pdf_id: UUID | None = Field(default=None, description="Referência ao documento PDF original")
    main_concepts: list[ConceptNode] = Field(
        default_factory=list, description="Conceitos principais identificados na aula"
    )
    prerequisites: list[Prerequisite] = Field(
        default_factory=list, description="Lista detalhada de todos os pré-requisitos identificados"
    )

    model_config = ConfigDict(from_attributes=True)
