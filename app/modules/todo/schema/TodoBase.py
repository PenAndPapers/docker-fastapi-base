from pydantic import BaseModel, Field, validator
from ..constants import (
    TodoSeverityEnum,
    TodoStatusEnum,
)


class TodoSchemaBase(BaseModel):
    model_config = {
        "from_attributes": True,
        "extra": "forbid",
    }


class TodoBase(TodoSchemaBase):
    title: str = Field(
        ...,
        min_length=10,
        max_length=200,
        description="The title of the todo (10-200 characters)",
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="The description of the todo (max 500 characters)",
    )
    severity: TodoSeverityEnum = Field(
        TodoSeverityEnum.LOW,
        description="The severity of the todo",
    )
    status: TodoStatusEnum = Field(
        TodoStatusEnum.TODO,
        description="The status of the todo",
    )

    @validator("title")
    def title_must_be_valid(cls, title: str):
        title = title.strip()
        if not title:
            raise ValueError("Title cannot be empty or just whitespace")
        return title
