from enum import Enum


class UserRoleEnum(str, Enum):
    ADMIN = "admin"
    USER = "user"


class UserStatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class GenderEnum(str, Enum):
    MALE = "male"
    FEMALE = "female"
