"""Repositório para operações de banco de dados relacionadas a PDFs."""

from uuid import UUID

from backend.domain.models.pdf import PDFDocument
from backend.infrastructure.database import execute_query


async def save_pdf_metadata(pdf: PDFDocument) -> PDFDocument:
    """
    Salva os metadados de um PDF no banco de dados.

    Args:
        pdf: Instância do modelo de domínio PDFDocument.

    Returns:
        PDFDocument: O documento salvo.
    """
    query = """
        INSERT INTO pdf_documents (id, hash, filename, size, bucket_key, content_text)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (hash) DO UPDATE
        SET filename = EXCLUDED.filename,
            updated_at = NOW()
        RETURNING id, created_at, updated_at
    """

    result = await execute_query(
        query, pdf.id, pdf.hash, pdf.filename, pdf.size, pdf.bucket_key, pdf.content_text
    )

    if result:
        row = result[0]
        pdf.id = row["id"]
        pdf.created_at = row["created_at"]
        pdf.updated_at = row["updated_at"]

    return pdf


async def get_pdf_by_hash(file_hash: str) -> PDFDocument | None:
    """
    Busca um PDF pelo seu hash SHA-256.

    Args:
        file_hash: Hash do arquivo.

    Returns:
        Optional[PDFDocument]: Documento encontrado ou None.
    """
    query = "SELECT * FROM pdf_documents WHERE hash = $1"
    result = await execute_query(query, file_hash)

    if not result:
        return None

    row = result[0]
    return PDFDocument(
        id=row["id"],
        hash=row["hash"],
        filename=row["filename"],
        size=row["size"],
        bucket_key=row["bucket_key"],
        content_text=row["content_text"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


async def get_pdf_by_id(pdf_id: UUID) -> PDFDocument | None:
    """
    Busca um PDF pelo seu ID único.

    Args:
        pdf_id: UUID do documento.

    Returns:
        Optional[PDFDocument]: Documento encontrado ou None.
    """
    query = "SELECT * FROM pdf_documents WHERE id = $1"
    result = await execute_query(query, pdf_id)

    if not result:
        return None

    row = result[0]
    return PDFDocument(
        id=row["id"],
        hash=row["hash"],
        filename=row["filename"],
        size=row["size"],
        bucket_key=row["bucket_key"],
        content_text=row["content_text"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )
