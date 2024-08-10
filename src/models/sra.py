# src/models/sra.py
from pydantic import BaseModel
from typing import List, Optional


class Task(BaseModel):
    id: str
    name: str
    duration: int
    predecessors: List[str]


class ProjectSchedule(BaseModel):
    project_id: str
    tasks: List[Task]


class SRARunRequest(BaseModel):
    project_id: str
    iterations: Optional[int] = 1000
    confidence_level: Optional[float] = 0.85


class SRARunResponse(BaseModel):
    project_id: str
    estimated_duration: int
    confidence_level: float


class NewSchedule(BaseModel):
    type: str
