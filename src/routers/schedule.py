# src/routers/sra.py
from fastapi import APIRouter, HTTPException, status
from ..models.sra import  NewSchedule
from ..lib.openai import generate_schedule
from ..lib import cache
from ..lib.cache import ScheduleNotFoundError
import logging

logger = logging.getLogger('app')

router = APIRouter(
    prefix="/schedule",
    tags=["schedule"]
)

@router.post("/")
async def add_schedule(new: NewSchedule):
    """
    generate schedule for a type of construction

    """

    try:
        schedule = await generate_schedule(new.type)
        schedule_id = cache.add_schedule(schedule)

        return {"message": f"Project schedule added successfully for type {new.type}",
                "schedule": schedule, "schedule_id": schedule_id}

    except Exception as e:
        logger.error(f"schedule generation failed {e}")
        raise HTTPException(
            status_code=500, detail="schedule generation failed")


@router.get("/{schedule_id}")
async def get_schedule(schedule_id: str):
    """
    get schedule per id

    """

    try:
        schedule = cache.get_schedule(schedule_id)

        return {"message": f" successfully got project schedule",
                "schedule": schedule, "schedule_id": schedule_id}
        
    except ScheduleNotFoundError:
        logger.warning(f"Schedule not found: {schedule_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with ID {schedule_id} not found"
        )

    except Exception as e:
        logger.warning(f"schedule get failed {e}")
        raise HTTPException(status_code=500, detail="")
    
    
@router.delete("/{schedule_id}")
async def remove_schedule(schedule_id: str):
    """
    remove schedule
    
    """

    try:
        
        cache.remove_schedule(schedule_id)
        return {"message": f"schedule removed {schedule_id}"}
    
    except:
        logger.error(f"schedule removal failed!{schedule_id}")
        raise HTTPException(status_code=500, detail="unknown error")
    
@router.delete("/")
async def remove_all_schedule():
    """
    remove all schedule
    
    """

    try:
        
        cache.remove_schedules()
        return {"message": f"all schedules removed"}
    
    except:
        logger.error(f"schedule removal failed!")
        raise HTTPException(status_code=500, detail="unknown error")