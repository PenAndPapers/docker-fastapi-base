from enum import Enum


class TokenTypeEnum(str, Enum):
    BEARER = "bearer"
    ACCESS = "access"
    REFRESH = "refresh"
