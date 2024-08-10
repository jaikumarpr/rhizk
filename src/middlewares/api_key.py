# src/middlewares/api_key.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import secrets

API_KEY_NAME = "X-API-Key"
API_KEY = secrets.token_urlsafe(32)

print(f"Generated API Key: {API_KEY}")

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in ["/docs", "/openapi.json", "/public"]:
            return await call_next(request)
        
        api_key = request.headers.get(API_KEY_NAME)
        if api_key != API_KEY:
            raise HTTPException(status_code=403, detail="Could not validate API key")
        
        return await call_next(request)