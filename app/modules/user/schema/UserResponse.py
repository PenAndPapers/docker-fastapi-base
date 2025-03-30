from datetime import datetime
from .UserBase import UserBase


class UserResponse(UserBase):
    model_config = {"from_attributes": True}
