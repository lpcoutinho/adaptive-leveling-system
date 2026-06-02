"""Client S3 para armazenamento de documentos (Minio)."""
import boto3
from botocore.client import Config
from backend.config import get_settings

_settings = get_settings()


def get_s3_client():
    """
    Retorna cliente S3 configurado para o endpoint local (Minio).

    Returns:
        boto3.client: Cliente S3 configurado.
    """
    return boto3.client(
        "s3",
        endpoint_url=_settings.s3_endpoint_url,
        aws_access_key_id=_settings.aws_access_key_id,
        aws_secret_access_key=_settings.aws_secret_access_key,
        config=Config(signature_version="s3v4"),
        region_name=_settings.aws_region,
    )


async def list_buckets() -> list[str]:
    """
    Lista todos os buckets S3 disponíveis.

    Returns:
        list[str]: Lista com os nomes dos buckets.
    """
    client = get_s3_client()
    response = client.list_buckets()
    return [b["Name"] for b in response.get("Buckets", [])]


async def create_bucket(bucket_name: str) -> None:
    """
    Cria um novo bucket S3 se ele ainda não existir.

    Args:
        bucket_name: Nome do bucket a ser criado.
    """
    client = get_s3_client()
    try:
        client.create_bucket(Bucket=bucket_name)
    except (client.exceptions.BucketAlreadyOwnedByYou, client.exceptions.BucketAlreadyExists):
        pass


async def delete_bucket(bucket_name: str) -> None:
    """
    Remove um bucket S3 existente.

    Args:
        bucket_name: Nome do bucket a ser removido.
    """
    client = get_s3_client()
    client.delete_bucket(Bucket=bucket_name)


async def bucket_exists(bucket_name: str) -> bool:
    """
    Verifica a existência de um bucket específico.

    Args:
        bucket_name: Nome do bucket.

    Returns:
        bool: True se o bucket existir e for acessível.
    """
    client = get_s3_client()
    try:
        client.head_bucket(Bucket=bucket_name)
        return True
    except Exception:
        return False


async def upload_object(bucket: str, key: str, content: bytes) -> None:
    """
    Faz o upload de um objeto (bytes) para um bucket S3.

    Args:
        bucket: Nome do bucket de destino.
        key: Chave (nome/caminho) do objeto no bucket.
        content: Conteúdo do objeto em bytes.
    """
    client = get_s3_client()
    client.put_object(Bucket=bucket, Key=key, Body=content)


async def download_object(bucket: str, key: str) -> bytes:
    """
    Faz o download de um objeto do S3.

    Args:
        bucket: Nome do bucket de origem.
        key: Chave do objeto no bucket.

    Returns:
        bytes: Conteúdo do objeto baixado.
    """
    client = get_s3_client()
    response = client.get_object(Bucket=bucket, Key=key)
    return response["Body"].read()


async def delete_object(bucket: str, key: str) -> None:
    """
    Remove um objeto específico de um bucket S3.

    Args:
        bucket: Nome do bucket.
        key: Chave do objeto a ser removido.
    """
    client = get_s3_client()
    client.delete_object(Bucket=bucket, Key=key)


async def ping_s3() -> bool:
    """
    Testa a conectividade com o serviço S3/Minio.

    Returns:
        bool: True se a conexão estiver saudável.
    """
    try:
        client = get_s3_client()
        client.list_buckets()
        return True
    except Exception as e:
        print(f"S3 ping failed: {e}")
        return False
