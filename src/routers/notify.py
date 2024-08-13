# src/routers/sra.py
from fastapi import APIRouter, HTTPException, status
import logging

logger = logging.getLogger('app')

router = APIRouter(
    prefix="/notify",
    tags=["notify"]
)


@router.get("/slideview")
async def notify_slide_view():

    try:
        logger.info("slide viewed")
        return {"message": f"thanks for viewing"}
    except:
        logger.error("notify failed")
        raise HTTPException(status_code=500, detail="unknown error")