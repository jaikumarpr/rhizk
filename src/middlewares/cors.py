# src/middlewares/cors.py
from fastapi.middleware.cors import CORSMiddleware

def add_cors_middleware(app):
    origins = [
        "http://localhost",
        "http://localhost:8080",
    ]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )