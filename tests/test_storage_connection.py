"""Testes de conexão S3 via floci."""
import pytest


@pytest.mark.asyncio
class TestS3Connection:
    """Testes de conexão com S3."""

    async def test_s3_client_created(self):
        """Testa que cliente S3 é criado."""
        from backend.infrastructure.storage import get_s3_client

        client = get_s3_client()
        assert client is not None

    async def test_s3_list_buckets(self):
        """Testa listagem de buckets."""
        from backend.infrastructure.storage import list_buckets

        buckets = await list_buckets()
        assert isinstance(buckets, list)

    async def test_s3_create_and_delete_bucket(self):
        """Testa criação e remoção de bucket."""
        from backend.infrastructure.storage import create_bucket, delete_bucket, bucket_exists

        bucket_name = "test-bucket-123"

        # Criar bucket
        await create_bucket(bucket_name)
        assert await bucket_exists(bucket_name) is True

        # Deletar bucket
        await delete_bucket(bucket_name)
        assert await bucket_exists(bucket_name) is False

    async def test_s3_upload_and_download(self):
        """Testa upload/download de objeto."""
        from backend.infrastructure.storage import (
            create_bucket,
            upload_object,
            download_object,
            delete_object,
        )

        bucket_name = "test-upload-bucket"
        key = "test.txt"
        content = b"Hello S3 from floci!"

        # Criar bucket
        await create_bucket(bucket_name)

        # Upload
        await upload_object(bucket_name, key, content)

        # Download
        downloaded = await download_object(bucket_name, key)
        assert downloaded == content

        # Limpar
        await delete_object(bucket_name, key)

    async def test_s3_ping(self):
        """Testa ping no S3 retorna sucesso."""
        from backend.infrastructure.storage import ping_s3

        is_healthy = await ping_s3()
        assert is_healthy is True
