# src/routers/sra.py
from fastapi import APIRouter, HTTPException, status
from ..lib import cache
from ..lib.cache import ScheduleNotFoundError
from ..lib.sra import perform_sra, SRACalculationError
import logging

logger = logging.getLogger('app')

router = APIRouter(
    prefix="/sra",
    tags=["SRA"]
)


@router.get("/{schedule_id}")
async def get_project_sra(schedule_id: str):
    """
    get sra result

    """

    try:

        schedule = cache.get_schedule(schedule_id)
        sra_result = perform_sra(schedule)

        return {"message": f"sra simulation succesfull",
                "schedule_id": schedule_id, "sra_result": sra_result}

    except ScheduleNotFoundError:
        logger.warning(f"Schedule not found: {schedule_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Schedule with ID {schedule_id} not found")

    except SRACalculationError as e:
        raise HTTPException(status_code=422, detail=str(e))

    except Exception as e:
        logger.error("schedule sra result failed!")
        raise HTTPException(status_code=500, detail="unknown error")
