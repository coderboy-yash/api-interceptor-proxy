from fastapi import FastAPI, HTTPException,Response
from fastapi.responses import StreamingResponse
import httpx
import uuid
import time
from io import BytesIO

from storage.minio_client import put_raw_object, put_metadata
from core.config import EXTERNAL_BASE_URL, EXTERNAL_API_KEY, HERE_BASE_URL, HERE_USERNAME, HERE_PASSWORD, PATH_ONE, PATH_TWO, PATH_THREE 

app = FastAPI(title="Proxy Service")

# -------------------------------------------------
# CONFIG: endpoint → upstream path → filename
# --------------------,-----------------------------
# ENDPOINT_CONFIG = {
#     "test":{
#         "path": PATH_ONE,
#         "filename": "test.gz",
#     },
#     "india_part1": {
#         "path": "/api/v1/live-traffic/india-part1of",
#         "filename": "india-part1of3.gz",
#     },
#     "india_part2": {
#         "path": "/api/v1/live-traffic/india-part2of3",
#         "filename": "india-part2of3.gz",
#     },
#     "india_part3": {
#         "path": "/api/v1/live-traffic/india-part3of3",
#         "filename": "india-part3of3.gz",
#     },
# }


# -------------------------------------------------
# SHARED proxy function (THE core logic)
# -------------------------------------------------
async def proxy_external(
    *,
    base_url: str,
    path: str,
    filename: str,
    params: dict | None = None,
    basic_auth: tuple | None = None,
):
    object_id = str(uuid.uuid4())
    start = time.time()

    url = f"{base_url}{path}"
    buffer = BytesIO()
    content_type = "application/octet-stream"

    async def stream():
        nonlocal content_type

        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "GET",
                url,
                params=params,
                auth=basic_auth,
            ) as resp:
                if resp.status_code != 200:
                    raise HTTPException(resp.status_code, "Upstream failed")

                content_type = resp.headers.get(
                    "content-type", "application/octet-stream"
                )

                async for chunk in resp.aiter_bytes():
                    buffer.write(chunk)
                    yield chunk

        raw = buffer.getvalue()

        put_raw_object(object_id, raw, content_type)
        put_metadata(
            object_id,
            {
                "source_url": url,
                "path": path,
                "filename": filename,
                "status_code": 200,
                "content_type": content_type,
                "size_bytes": len(raw),
                "latency_ms": int((time.time() - start) * 1000),
                "timestamp": time.time(),
            },
        )

    return StreamingResponse(
        stream(),
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "X-Object-ID": object_id,
        },
    )


# -------------------------------------------------
# ENDPOINTS (thin, readable, zero logic)
# -------------------------------------------------
# HERE_URL = f"{HERE_BASE_URL}/{PATH_ONE}"

@app.get("/live-traffic/india-part1of3")
async def traffic():
    return await proxy_external(
        base_url=HERE_BASE_URL,
        path=f"/{PATH_ONE}",
        filename="india-part1of3.gz",
        basic_auth=(HERE_USERNAME, HERE_PASSWORD),
    )
     
@app.get("/live-traffic/india-part2of3")
async def traffic():
    return await proxy_external(
        base_url=HERE_BASE_URL,
        path=f"/{PATH_TWO}",
        filename="india-part2of3.gz",
        basic_auth=(HERE_USERNAME, HERE_PASSWORD),
    )
     
@app.get("/live-traffic/india-part3of3")
async def traffic():
    return await proxy_external(
        base_url=HERE_BASE_URL,
        path=f"/{PATH_THREE}",
        filename="india-part3of3.gz",
        basic_auth=(HERE_USERNAME, HERE_PASSWORD),
    )
     

# @app.get("/traffic/india/part1")
# async def india_part1():
#     cfg = ENDPOINT_CONFIG["india_part1"]
#     return await proxy_external(cfg["path"], cfg["filename"])


# @app.get("/traffic/india/part2")
# async def india_part2():
#     cfg = ENDPOINT_CONFIG["india_part2"]
#     return await proxy_external(cfg["path"], cfg["filename"])


# @app.get("/traffic/india/part3")
# async def india_part3():
#     cfg = ENDPOINT_CONFIG["india_part3"]
#     return await proxy_external(cfg["path"], cfg["filename"])
