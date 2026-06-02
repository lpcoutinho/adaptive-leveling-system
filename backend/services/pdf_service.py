"""Serviço de negócio para processamento de arquivos PDF."""

import hashlib
import io

from pypdf import PdfReader

from backend.domain.models.pdf import PDFDocument
from backend.infrastructure.repository.pdf_repository import get_pdf_by_hash, save_pdf_metadata
from backend.infrastructure.storage.pdf_storage import upload_pdf


def calculate_hash(content: bytes) -> str:
    """Calcula o hash SHA-256 de um conteúdo binário."""
    return hashlib.sha256(content).hexdigest()


def extract_text_from_pdf(content: bytes) -> str:
    """
    Extrai o texto de um PDF em memória.

    Args:
        content: Conteúdo binário do PDF.

    Returns:
        str: Texto extraído.
    """
    pdf_file = io.BytesIO(content)
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    return text.strip()


async def process_pdf(content: bytes, filename: str) -> PDFDocument:
    """
    Orquestra o processamento completo de um PDF.

    Lógica:
    1. Calcula hash.
    2. Verifica se já existe no banco.
    3. Se não existe:
       - Sobe para o S3.
       - Extrai texto.
       - Salva metadados no banco.
    4. Retorna o documento (novo ou existente).

    Args:
        content: Bytes do arquivo.
        filename: Nome original.

    Returns:
        PDFDocument: Objeto de domínio preenchido.
    """
    file_hash = calculate_hash(content)

    # Verificação de Idempotência
    existing_pdf = await get_pdf_by_hash(file_hash)
    if existing_pdf:
        return existing_pdf

    # Processamento de novo arquivo
    # 1. Upload S3
    bucket_key = await upload_pdf(filename, content)

    # 2. Extração de texto
    text = extract_text_from_pdf(content)

    # 3. Persistência
    pdf_doc = PDFDocument(
        hash=file_hash,
        filename=filename,
        size=len(content),
        bucket_key=bucket_key,
        content_text=text,
    )

    saved_pdf = await save_pdf_metadata(pdf_doc)
    return saved_pdf
