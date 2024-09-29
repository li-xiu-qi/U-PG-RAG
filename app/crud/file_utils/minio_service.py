import hashlib
import io
import json
from datetime import timedelta
from fastapi import HTTPException, UploadFile
from minio import Minio
from config import ServeConfig
import hashlib
from fastapi import UploadFile


async def generate_object_key(file: UploadFile) -> str:
    hash_sha256 = hashlib.sha256()
    chunk_size = 8192

    while chunk := await file.read(chunk_size):
        hash_sha256.update(chunk)

    await file.seek(0)
    return hash_sha256.hexdigest()


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

    def __init__(self, minio_client: Minio, bucket_name: str, public: bool = False):
        self.minio_client = minio_client
        self.bucket_name = bucket_name
        self.public = public
        self._ensure_bucket()
        if self.public:
            self._set_bucket_policy()

    def _ensure_bucket(self):
        if not self.minio_client.bucket_exists(self.bucket_name):
            self.minio_client.make_bucket(self.bucket_name, location=self.minio_region)

    def _set_bucket_policy(self):
        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"]
                }
            ]
        }
        policy_json = json.dumps(policy)
        self.minio_client.set_bucket_policy(self.bucket_name, policy_json)

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

    async def generate_file_url(self, object_key: str, expiry: int | None = None) -> str:
        try:
            if self.public:
                return self.generate_public_url(object_key)
            if expiry is None:
                raise Exception("Expiry time is required for private files")
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

    def generate_public_url(self, object_key: str) -> str:
        return f"http://{ServeConfig.minio_endpoint}/{self.bucket_name}/{object_key}"
