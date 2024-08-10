# src/middlewares/api_key.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import os

API_KEY_NAME = "X-API-Key"

API_KEY = os.getenv("API_KEY")

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/docs", "/openapi.json", "/public"]:
            return await call_next(request)
        
        api_key = request.headers.get(API_KEY_NAME)
        if api_key != API_KEY:
            raise HTTPException(status_code=403, detail="Could not validate API key")
        
        return await call_next(request)