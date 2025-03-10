from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    id: int
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str | None = None
    gender: str | None = None
    date_of_birth: datetime | None = None
    address: str | None = None
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}
