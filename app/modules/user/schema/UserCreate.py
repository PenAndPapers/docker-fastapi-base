from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone_number: str | None = None
    gender: str | None = None
    date_of_birth: datetime | None = None
    address: str | None = None
    is_verified: bool = False

    model_config = {"from_attributes": True}
