# src/main.py
from fastapi import FastAPI
from .middlewares.cors import add_cors_middleware
from .middlewares.security_headers import SecurityHeadersMiddleware
# from .middlewares.api_key import APIKeyMiddleware
from .middlewares.rate_limiter import RateLimitMiddleware
from .routers.sra import router as sra_router
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

app = FastAPI()

# Add CORS middleware
add_cors_middleware(app)

# Add security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Add API Key middleware
# app.add_middleware(APIKeyMiddleware)

# Add Rate Limit middleware
app.add_middleware(RateLimitMiddleware, limit=100)

# Include the SRA router with a version prefix
app.include_router(sra_router, prefix="/v1")

@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to the Schedule Risk Analysis API"}

@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "OK"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)