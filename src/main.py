# src/main.py
from .helpers.logger import logger, init as log_init
from contextlib import asynccontextmanager
from . import routers
from . import middlewares
import os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
log_init()

port = os.getenv("PORT")
host = os.getenv("HOST")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("application started")

    yield

    logger.info("application shutdown")

app = FastAPI(lifespan=lifespan)

# add all middlewares
middlewares.init(app)

# Include all routers from the folder routers
routers.init(app, "v1")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host, port)
