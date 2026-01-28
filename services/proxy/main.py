from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import uuid
import time
from io import BytesIO
from fastapi.middleware.gzip import GZipMiddleware

from storage.minio_client import upload_xml_bytes, upload_json
from core.config import EXTERNAL_BASE_URL, EXTERNAL_PATH, EXTERNAL_API_KEY

app = FastAPI(title="Proxy Service")
app.add_middleware(GZipMiddleware, minimum_size=1024)


@app.get("/proxy/external/xml")
async def proxy_external_xml(background_tasks: BackgroundTasks):
    if not all([EXTERNAL_BASE_URL, EXTERNAL_PATH, EXTERNAL_API_KEY]):
        raise HTTPException(500, "External API configuration missing")

    request_id = str(uuid.uuid4())
    start_time = time.time()

    url = f"{EXTERNAL_BASE_URL}{EXTERNAL_PATH}"
    params = {"api_key": EXTERNAL_API_KEY}

    async def stream_and_capture():
        buffer = BytesIO()

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream("GET", url, params=params) as response:
                if response.status_code != 200:
                    raise HTTPException(response.status_code, "External API failed")

                async for chunk in response.aiter_bytes():
                    buffer.write(chunk)   # capture for MinIO
                    yield chunk            # stream to client

        # after streaming finishes → store in MinIO
        xml_bytes = buffer.getvalue()

        background_tasks.add_task(
            upload_xml_bytes,
            f"responses/{request_id}.xml",
            xml_bytes
        )

        background_tasks.add_task(
            upload_json,
            f"metadata/{request_id}.json",
            {
                "url": url,
                "status_code": 200,
                "latency_ms": int((time.time() - start_time) * 1000),
                "size_bytes": len(xml_bytes),
                "timestamp": time.time(),
            }
        )

    return StreamingResponse(
        stream_and_capture(),
        media_type="application/xml",
        headers={
            "X-Request-ID": request_id,
        }
    )
