"""Modelos de domínio para documentos PDF."""

from pydantic import ConfigDict

from backend.domain.models.common import TimestampModel, UUIDModel


class PDFDocument(UUIDModel, TimestampModel):
    """Representa um documento PDF processado e armazenado no sistema."""

    hash: str
    filename: str
    size: int
    bucket_key: str
    content_text: str | None = None

    model_config = ConfigDict(from_attributes=True)
