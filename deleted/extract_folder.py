from minio import Minio
import json
import os
from dotenv import load_dotenv

load_dotenv()

client = Minio(
    os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False
)

BUCKET = os.getenv("MINIO_BUCKET")
FOLDER = "responses/"
OUTPUT_DIR = "output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

for obj in client.list_objects(BUCKET, prefix=FOLDER, recursive=True):
    response = client.get_object(BUCKET, obj.object_name)
    data = json.loads(response.read().decode("utf-8"))

    filename = obj.object_name.replace("/", "_")
    with open(f"{OUTPUT_DIR}/{filename}", "w") as f:
        json.dump(data, f, indent=2)

    print(f"Extracted: {obj.object_name}")
