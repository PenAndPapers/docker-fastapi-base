from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
from app.core import BasePaginationParams
from ..constants import (
    TodoSeverityEnum,
    TodoStatusEnum,
)
from ..model import Todo


class TodoSchemaBase(BaseModel):
    model_config = {
        "from_attributes": True
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


class TodoCreate(TodoBase):
    pass


class TodoUpdate(TodoBase):
    severity: TodoSeverityEnum | None = Field(
        None,
        description="The severity of the todo",
    )
    status: TodoStatusEnum | None = Field(
        None,
        description="The status of the todo",
    )


class TodoResponse(TodoBase):
    id: int
    title: str
    description: str | None
    severity: TodoSeverityEnum
    status: TodoStatusEnum
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class TodoSortFields(str, Enum):
    ID = "id"
    TITLE = "title"
    DESCRIPTION = "description"
    STATUS = "status"
    SEVERITY = "severity"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"


class TodoPaginationParams(BasePaginationParams):
    """
    This represents the filters that can be applied to the todos.
    - title
    - description
    - status
    - severity

    Defined in the BasePaginationParams:
    - created_at
    - updated_at
    """

    # Override sort_by with table-specific fields
    sort_by: TodoSortFields = Field(default=TodoSortFields.CREATED_AT)
    title: str | None = None
    description: str | None = None
    status: TodoStatusEnum | None = None
    severity: TodoSeverityEnum | None = None

    model_config = {
        "from_attributes": True,
        "model": Todo
    }
