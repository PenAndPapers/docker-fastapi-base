from .UserBase import UserBase


class UserCreateRequest(UserBase):
    id: int | None = None

    model_config = {"from_attributes": True}

