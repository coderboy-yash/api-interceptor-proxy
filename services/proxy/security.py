from fastapi import HTTPException, status, Query
from core.config import EXTERNAL_API_KEY
# API_KEY = "super   # move to ENV later

def verify_api_key(api_key: str = Query(...)):
    if api_key != EXTERNAL_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )
