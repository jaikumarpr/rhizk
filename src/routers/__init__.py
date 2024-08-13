import os
import importlib
from fastapi import FastAPI, APIRouter
def init(app: FastAPI, api_version: str):
    module_names = [
        os.path.splitext(file)[0]
        for file in os.listdir(os.path.dirname(__file__))
        if file.endswith(".py") and file != "__init__.py"
    ]

    for module_name in module_names:
        try:
            module = importlib.import_module(
                f".{module_name}", package=__name__)
            if hasattr(module, "router") and isinstance(module.router, APIRouter):
                app.include_router(module.router, prefix=f"/{api_version}")
            else:
                print(f"Warning: Module {module_name} does not have a valid router attribute")
        except ImportError as e:
            print(f"Error importing module {module_name}: {e}")
    
    add_index_routes(app)


def add_index_routes(app: FastAPI):
    @app.get("/", tags=["root"])
    async def root():
        return {"message": "Welcome to the Schedule Risk Analysis API"}

    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "OK"}