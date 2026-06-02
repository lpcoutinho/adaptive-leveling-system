"""Endpoints da API para gerenciamento de documentos PDF."""

from uuid import UUID

from fastapi import APIRouter, File, HTTPException, UploadFile

from backend.api.schemas.pdf import PDFResponse, PDFUploadResponse
from backend.infrastructure.repository.pdf_repository import get_pdf_by_hash, get_pdf_by_id
from backend.services.pdf_service import process_pdf

router = APIRouter(prefix="/pdf", tags=["PDF Management"])


@router.post("/upload", response_model=PDFUploadResponse, status_code=201)
async def upload_pdf_file(file: UploadFile = File(...)):
    """
    Realiza o upload de um arquivo PDF, extrai texto e salva metadados.

    A implementação utiliza idempotência baseada no hash do arquivo.
    """
    filename = file.filename or "unnamed.pdf"

    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Apenas arquivos PDF são permitidos.")

    content = await file.read()
    if not content.startswith(b"%PDF-"):
        raise HTTPException(status_code=400, detail="O arquivo não parece ser um PDF válido.")

    try:
        pdf_doc = await process_pdf(content, filename)
        return PDFUploadResponse(
            id=pdf_doc.id, filename=pdf_doc.filename, hash=pdf_doc.hash, status="processed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar PDF: {str(e)}") from e


@router.get("/{pdf_id}", response_model=PDFResponse)
async def get_pdf(pdf_id: UUID):
    """Retorna os metadados de um PDF pelo ID."""
    pdf = await get_pdf_by_id(pdf_id)
    if not pdf:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return pdf


@router.get("/hash/{file_hash}", response_model=PDFResponse)
async def get_pdf_by_file_hash(file_hash: str):
    """Busca um PDF pelo seu hash SHA-256."""
    pdf = await get_pdf_by_hash(file_hash)
    if not pdf:
        raise HTTPException(status_code=404, detail="Documento não encontrado.")
    return pdf
