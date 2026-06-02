"""Modelos base compartilhados entre diferentes domínios."""

from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TimestampModel(BaseModel):
    """Mix-in para adicionar campos de data de criação e atualização."""

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class UUIDModel(BaseModel):
    """Mix-in para adicionar campo ID com UUID."""

    id: UUID = Field(default_factory=uuid4)
