import hashlib
import io
from datetime import timedelta
from fastapi import HTTPException, UploadFile
from minio import Minio
from config import ServeConfig


def generate_object_key(file_content: bytes) -> str:
    return hashlib.sha256(file_content).hexdigest()


def init_minio_client():
    """初始化MinIO客户端"""
    minio_client = Minio(
        ServeConfig.minio_endpoint,
        access_key=ServeConfig.minio_access_key,
        secret_key=ServeConfig.minio_secret_key,
        secure=False,
        region=ServeConfig.minio_region
    )
    return minio_client


class MinIOFileService:
    minio_region = ServeConfig.minio_region

    def __init__(self, minio_client: Minio, bucket_name: str):
        self.minio_client = minio_client
        self.bucket_name = bucket_name
        self._ensure_bucket()

    def _ensure_bucket(self):
        if not self.minio_client.bucket_exists(self.bucket_name):
            self.minio_client.make_bucket(self.bucket_name, location=self.minio_region)

    async def upload_file(self, file: UploadFile, object_key: str) -> None:
        try:
            file_content = await file.read()
            file_size = len(file_content)
            if file_size <= 0:
                raise HTTPException(status_code=400, detail="Invalid file size")

            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_key,
                data=io.BytesIO(file_content),
                length=file_size,
                content_type=file.content_type
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def generate_presigned_url(self, object_key: str, expiry: int) -> str:
        try:
            return self.minio_client.presigned_get_object(
                bucket_name=self.bucket_name,
                object_name=object_key,
                expires=timedelta(seconds=expiry)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_file(self, object_key: str) -> None:
        try:
            self.minio_client.remove_object(bucket_name=self.bucket_name, object_name=object_key)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
