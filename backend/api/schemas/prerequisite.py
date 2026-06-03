"""Schemas Pydantic para validação de dados de API relacionados a pré-requisitos."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PrerequisiteSchema(BaseModel):
    """Schema para exibição de um pré-requisito."""

    name: str
    description: str
    importance: str
    topics: list[str]


class ConceptNodeSchema(BaseModel):
    """Schema para exibição de um conceito da aula."""

    name: str
    description: str
    prerequisites: list[str]


class KnowledgeGraphResponse(BaseModel):
    """Schema para resposta completa do grafo de conhecimento."""

    id: UUID
    pdf_id: UUID
    main_concepts: list[ConceptNodeSchema]
    prerequisites: list[PrerequisiteSchema]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
