import boto3
from botocore.config import Config
from app.config import settings

s3_client = boto3.client(
    "s3",
    endpoint_url=f\"{'https' if settings.STORAGE_SECURE else 'http'}://{settings.STORAGE_ENDPOINT}\",
    aws_access_key_id=settings.STORAGE_ACCESS_KEY,
    aws_secret_access_key=settings.STORAGE_SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name="us-east-1",
)


def get_storage():
    """Dependency injection for S3/MinIO storage."""
    return s3_client


async def ensure_bucket():
    """Create bucket if it doesn't exist."""
    try:
        s3_client.head_bucket(Bucket=settings.STORAGE_BUCKET)
    except Exception:
        s3_client.create_bucket(Bucket=settings.STORAGE_BUCKET)


async def upload_file(file_data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
    """Upload a file to storage and return the URL."""
    s3_client.put_object(
        Bucket=settings.STORAGE_BUCKET,
        Key=key,
        Body=file_data,
        ContentType=content_type,
    )
    return f\"{'https' if settings.STORAGE_SECURE else 'http'}://{settings.STORAGE_ENDPOINT}/{settings.STORAGE_BUCKET}/{key}\"


async def delete_file(key: str):
    """Delete a file from storage."""
    s3_client.delete_object(Bucket=settings.STORAGE_BUCKET, Key=key)
