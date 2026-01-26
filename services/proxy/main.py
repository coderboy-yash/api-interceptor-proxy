from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid
import time
import httpx

from storage.minio_client import upload_json
from core.config import EXTERNAL_BASE_URL

app = FastAPI(title="Proxy Service")


class ProxyRequest(BaseModel):
    method: str
    path: str
    query: dict | None = None
    headers: dict | None = None
    body: dict | None = None


@app.post("/proxy/external")
async def proxy_external(
    req: ProxyRequest,
    background_tasks: BackgroundTasks
):
    if not EXTERNAL_BASE_URL:
        raise HTTPException(status_code=500, detail="EXTERNAL_BASE_URL not configured")

    request_id = str(uuid.uuid4())
    start_time = time.time()

    url = f"{EXTERNAL_BASE_URL}{req.path}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.request(
            method=req.method.upper(),
            url=url,
            params=req.query,
            headers=req.headers,
            json=req.body
        )

    data = response.json()
    latency_ms = int((time.time() - start_time) * 1000)

    background_tasks.add_task(
        upload_json,
        f"responses/{request_id}.json",
        data
    )

    background_tasks.add_task(
        upload_json,
        f"metadata/{request_id}.json",
        {
            "method": req.method,
            "url": url,
            "status_code": response.status_code,
            "latency_ms": latency_ms,
            "timestamp": time.time(),
        }
    )

    return {
        "request_id": request_id,
        "data": data,
        "latency_ms": latency_ms
    }
