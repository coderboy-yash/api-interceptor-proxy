import os
from dotenv import load_dotenv

load_dotenv()

EXTERNAL_BASE_URL = os.getenv("EXTERNAL_BASE_URL")

MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_BUCKET = os.getenv("MINIO_BUCKET")
MINIO_SECURE = False

# ///
EXTERNAL_PATH = os.getenv("EXTERNAL_PATH")
EXTERNAL_API_KEY = os.getenv("EXTERNAL_API_KEY")

