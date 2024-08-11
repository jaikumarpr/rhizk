# src/routers/sra.py
from fastapi import APIRouter, HTTPException
from ..models.sra import ProjectSchedule, SRARunRequest, SRARunResponse, NewSchedule
from ..lib.openai import get_schedule
from ..lib.cache import get_schedule as get_schedue_from_cache, cache_schedule
from ..lib.sra import perform_sra
from ..helpers.logger import logger

router = APIRouter()


@router.post("/schedule", tags=["SRA"])
async def add_project_schedule(new: NewSchedule):
    """
    generate schedule for a type of construction

    """

    try:
        schedule = await get_schedule(new.type)
        schedule_id = cache_schedule(schedule)

        return {"message": f"Project schedule added successfully for type {new.type}",
                "schedule": schedule, "schedule_id": schedule_id}

    except Exception as e:
        logger.error(f"schedule generation failed {e}")
        raise HTTPException(
            status_code=500, detail="schedule generation failed")


@router.get("/schedule/{schedule_id}", tags=["SRA"])
async def get_project_schedule(schedule_id: str):
    """
    get schedule per id

    """

    try:
        schedule = get_schedue_from_cache(schedule_id)
        if (not schedule):
            raise HTTPException(status_code=404, detail="schedule not found")

        schedule_id = cache_schedule(schedule)

        return {"message": f" successfully got project schedule",
                "schedule": schedule, "schedule_id": schedule_id}

    except Exception as e:
        logger.error(f"schedule get failed {e}")
        raise HTTPException(status_code=500, detail="schedule not found")


@router.get("/sra/{schedule_id}", tags=["SRA"])
async def get_project_sra(schedule_id: str):
    """
    get sra result

    """

    try:

        schedule = get_schedue_from_cache(schedule_id)

        if (not schedule):
            raise HTTPException(status_code=404, detail="schedule not found")

        schedule_id = cache_schedule(schedule)

        sra_result = perform_sra(schedule)

        return {"message": f"sra simulation succesfull",
                "schedule_id": schedule_id, "sra_result": sra_result}
    except:
        logger.error("schedule sra result failed!")
        raise HTTPException(status_code=500, detail="sra analysis failed")


@router.get("/notify/slideview", tags=["SRA"])
async def notify_slide_view():

    try:
        logger.info("slide viewed")

        return {"message": f"thanks for viewing"}
    except:
        logger.error("notify failed")
        raise HTTPException(status_code=500, detail="failed not notify")
