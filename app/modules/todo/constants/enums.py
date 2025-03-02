"""
this file contains the enums for the todo module
"""

from enum import Enum


class TodoSeverityEnum(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class TodoStatusEnum(str, Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class TodoSortFieldsEnum(str, Enum):
    TITLE = "title"
    DESCRIPTION = "description"
    SEVERITY = "severity"
    STATUS = "status"
    CREATED_AT = "created_at"
    UPDATED_AT = "updated_at"
