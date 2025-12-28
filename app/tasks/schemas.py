from pydantic import BaseModel, Field, field_validator
from typing import Optional
from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskCreateModel(BaseModel):
    title: str = Field(..., min_length=1)
    description: str
    status: TaskStatus = TaskStatus.pending

    @field_validator("status")
    def status_validator(cls, v):
        if not v == "pending":
            raise ValueError("Status must be pending on creation")
        return v


class TaskUpdateModel(BaseModel):
    title: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
