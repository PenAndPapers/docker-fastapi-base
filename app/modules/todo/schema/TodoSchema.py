from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum
from app.core import BasePaginationParams
from ..constants import (
    SeverityEnum,
    StatusEnum,
)
from ..model import Todo


class TodoBase(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="The title of the todo (3-200 characters)",
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="The description of the todo (max 500 characters)",
    )
    severity: SeverityEnum = Field(
        SeverityEnum.LOW,
        description="The severity of the todo",
    )
    status: StatusEnum = Field(
        StatusEnum.TODO,
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


class TodoUpdate(BaseModel):
    title: str = Field(
        ...,
        min_length=3,
        max_length=100,
        description="The title of the todo (3-100 characters)",
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="The description of the todo (max 500 characters)",
    )
    severity: SeverityEnum = Field(
        SeverityEnum.LOW,
        description="The severity of the todo",
    )
    status: StatusEnum = Field(
        StatusEnum.TODO,
        description="The status of the todo",
    )


class TodoResponse(TodoBase):
    id: int
    title: str
    description: str | None
    severity: SeverityEnum
    status: StatusEnum
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


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
    status: StatusEnum | None = None
    severity: SeverityEnum | None = None

    class Config:
        model = Todo
