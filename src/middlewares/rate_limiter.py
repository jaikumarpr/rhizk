# src/middlewares/rate_limiter.py
from fastapi import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class RateLimiter:
    def __init__(self, limit: int = 100):
        self.limit = limit
        self.requests = {}

    def is_allowed(self, ip: str) -> bool:
        if ip not in self.requests:
            self.requests[ip] = 1
            return True
        if self.requests[ip] >= self.limit:
            return False
        self.requests[ip] += 1
        return True

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limit: int = 100):
        super().__init__(app)
        self.limiter = RateLimiter(limit)

    async def dispatch(self, request, call_next):
        if not self.limiter.is_allowed(request.client.host):
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        return await call_next(request)