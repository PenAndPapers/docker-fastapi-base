from datetime import datetime
from .TodoBase import TodoBase
from ..constants import TodoSeverityEnum, TodoStatusEnum


class TodoResponse(TodoBase):
    id: int
    title: str
    description: str | None
    severity: TodoSeverityEnum
    status: TodoStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
