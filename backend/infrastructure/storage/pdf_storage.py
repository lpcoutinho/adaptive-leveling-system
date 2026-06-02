"""Serviços de armazenamento S3 específicos para documentos PDF."""

from typing import cast

from backend.config import get_settings
from backend.infrastructure.storage import get_s3_client, upload_object

_settings = get_settings()


async def upload_pdf(filename: str, content: bytes) -> str:
    """
    Faz o upload de um PDF para o bucket padrão.

    Args:
        filename: Nome do arquivo (usado para compor a key).
        content: Conteúdo em bytes do PDF.

    Returns:
        str: A bucket_key (caminho) do arquivo no S3.
    """
    # Define a estrutura de pastas no S3: uploads/nome_do_arquivo
    bucket_key = f"uploads/{filename}"
    await upload_object(_settings.s3_bucket, bucket_key, content)
    return bucket_key


def generate_pdf_presigned_url(bucket_key: str, expiration: int = 3600) -> str:
    """
    Gera uma URL temporária para download seguro do PDF.

    Args:
        bucket_key: O caminho do arquivo no S3.
        expiration: Tempo de expiração em segundos (padrão 1h).

    Returns:
        str: URL de download.
    """
    client = get_s3_client()
    url = client.generate_presigned_url(
        "get_object",
        Params={"Bucket": _settings.s3_bucket, "Key": bucket_key},
        ExpiresIn=expiration,
    )
    return cast(str, url)
