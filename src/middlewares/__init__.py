from fastapi import FastAPI
from .api_key import APIKeyMiddleware
from fastapi.middleware.cors import CORSMiddleware
from ..config.cors_config import cors_config
from .httplog import LogRequestsMiddleware
from .security_headers import SecurityHeadersMiddleware
from .rate_limiter import RateLimitMiddleware


def init(app: FastAPI):
    app.add_middleware(LogRequestsMiddleware)
    app.add_middleware(CORSMiddleware, **cors_config)
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(APIKeyMiddleware)
    app.add_middleware(RateLimitMiddleware, limit=10)
