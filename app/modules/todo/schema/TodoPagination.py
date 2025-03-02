from pydantic import Field
from app.core import BasePaginationParams
from ..constants import (
    TodoSeverityEnum,
    TodoStatusEnum,
    TodoSortFieldsEnum,
)
from ..model import Todo


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
    sort_by: TodoSortFieldsEnum = Field(default=TodoSortFieldsEnum.CREATED_AT)
    title: str | None = None
    description: str | None = None
    status: TodoStatusEnum | None = None
    severity: TodoSeverityEnum | None = None

    model_config = {"from_attributes": True, "model": Todo}
