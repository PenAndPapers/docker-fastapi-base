from pydantic import Field
from .TodoBase import TodoBase
from ..constants import TodoSeverityEnum, TodoStatusEnum


class TodoUpdate(TodoBase):
    severity: TodoSeverityEnum | None = Field(
        None,
        description="The severity of the todo",
    )
    status: TodoStatusEnum | None = Field(
        None,
        description="The status of the todo",
    )
