"""Schemas Pydantic para validação de dados de API relacionados a PDFs."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class PDFBase(BaseModel):
    """Base para schemas de PDF."""

    filename: str = Field(..., description="Nome original do arquivo")
    size: int = Field(..., description="Tamanho do arquivo em bytes")


class PDFCreate(PDFBase):
    """Schema para criação de um novo registro de PDF."""

    hash: str = Field(..., description="Hash SHA-256 do arquivo")
    bucket_key: str = Field(..., description="Caminho do objeto no S3")
    content_text: str | None = Field(None, description="Texto extraído do PDF")


class PDFResponse(PDFBase):
    """Schema para resposta de dados de PDF."""

    id: UUID
    hash: str
    bucket_key: str
    content_text: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PDFUploadResponse(BaseModel):
    """Schema para resposta simplificada de upload."""

    id: UUID
    filename: str
    hash: str
    status: str = Field("processed", description="Status do processamento")
