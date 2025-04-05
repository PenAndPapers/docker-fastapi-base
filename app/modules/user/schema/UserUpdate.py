from .UserBase import UserBase


class UserUpdateRequest(UserBase):
    id: int | None = None

    model_config = {
        "from_attributes": True,
    }
