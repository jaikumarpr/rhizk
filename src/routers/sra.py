# src/routers/sra.py
from fastapi import APIRouter, HTTPException
from ..models.sra import ProjectSchedule, SRARunRequest, SRARunResponse, NewSchedule
from ..lib.openai import get_schedule
from ..lib.cache import get_schedule as get_schedue_from_cache, cache_schedule
from ..lib.sra import perform_sra

router = APIRouter()


@router.post("/schedule", tags=["SRA"])
async def add_project_schedule(new: NewSchedule):
    """
    generate schedule for a type of construction
    
    """
    schedule = await get_schedule(new.type) 
    
    schedule_id = cache_schedule(schedule)
    
    print(schedule)
    
    return {"message": f"Project schedule added successfully for type {new.type}",
            "schedule": schedule, "schedule_id": schedule_id}
    
@router.get("/schedule/{schedule_id}", tags=["SRA"])
async def get_project_schedule(schedule_id: str):
    """
    generate schedule for a type of construction
    
    """
    schedule = get_schedue_from_cache(schedule_id)
    
    schedule_id = cache_schedule(schedule)
    
    return {"message": f" successfully got project schedule",
            "schedule": schedule, "schedule_id": schedule_id}
    
@router.get("/sra/{schedule_id}", tags=["SRA"])
async def get_project_sra(schedule_id: str):
    """
    generate schedule for a type of construction
    
    """
    schedule = get_schedue_from_cache(schedule_id)

    
    schedule_id = cache_schedule(schedule)

    
    sra_result = perform_sra(schedule)
        
    return {"message": f"sra simulation succesfull",
             "schedule_id": schedule_id, "sra_result": sra_result}

