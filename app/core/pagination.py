from pydantic import BaseModel, Field
from datetime import date
from enum import Enum, IntEnum
from typing import Generic, TypeVar, List

T = TypeVar("T")
DATE_FORMAT = "YYYY-MM-DD"


class BaseSortOrder(str, Enum):
    ASC = "asc"
    DESC = "desc"


class PageSize(IntEnum):
    """Valid page size options"""

    SMALL = 10
    MEDIUM = 25
    LARGE = 50
    EXTRA_LARGE = 100


class BasePaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    current_page: int
    per_page: int
    pages: int
    has_next: bool
    has_prev: bool


class BasePaginationParams(BaseModel):
    # Pagination
    page: int = Field(default=1, ge=1)
    page_size: PageSize = Field(default=PageSize.SMALL)
    # Sorting
    sort_by: str = Field(default="created_at")
    sort_order: BaseSortOrder = Field(default=BaseSortOrder.DESC)

    # Default date range filters for all tables
    created_at_from: date | None = Field(None, description=DATE_FORMAT)
    created_at_to: date | None = Field(None, description=DATE_FORMAT)
    updated_at_from: date | None = Field(None, description=DATE_FORMAT)
    updated_at_to: date | None = Field(None, description=DATE_FORMAT)
