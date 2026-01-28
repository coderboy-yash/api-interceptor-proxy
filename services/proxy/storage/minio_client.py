import json
from io import BytesIO
from minio import Minio

from core.config import (
    MINIO_ENDPOINT,
    MINIO_ACCESS_KEY,
    MINIO_SECRET_KEY,
    MINIO_BUCKET,
    MINIO_SECURE,
)

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE,
)


def upload_json(object_name: str, data: dict):
    """
    Upload a JSON object to MinIO
    """
    raw = json.dumps(data).encode("utf-8")
    stream = BytesIO(raw)

    minio_client.put_object(
        bucket_name=MINIO_BUCKET,
        object_name=object_name,
        data=stream,
        length=len(raw),
        content_type="application/json",
    )

def upload_xml_bytes(object_name: str, data: bytes):
    minio_client.put_object(
        bucket_name=MINIO_BUCKET,
        object_name=object_name,
        data=BytesIO(data),
        length=len(data),
        content_type="application/xml"
    )
