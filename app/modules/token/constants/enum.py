from enum import Enum


class EnumTokenType(str, Enum):
    BEARER = "bearer"
    ACCESS = "access"
    REFRESH = "refresh"