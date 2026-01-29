# storage/minio_client.py
from minio import Minio
from io import BytesIO
import json

from core.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
)

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False,
)


def put_raw_object(object_id: str, data: bytes, content_type: str):
    client.put_object(
        bucket_name=MINIO_BUCKET,
        object_name=f"blobs/{object_id}",   # 👈 prefix = folder
        data=BytesIO(data),
        length=len(data),
        content_type=content_type,
    )


def put_metadata(object_id: str, payload: dict):
    raw = json.dumps(payload).encode("utf-8")

    client.put_object(
        bucket_name=MINIO_BUCKET,
        object_name=f"metadata/{object_id}.json",  # 👈 separate folder
        data=BytesIO(raw),
        length=len(raw),
        content_type="application/json",
    )

