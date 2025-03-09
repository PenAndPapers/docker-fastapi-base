from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


class AuthBase(BaseModel):
    email: EmailStr
    password: str

    model_config = {"from_attributes": True}

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        valid_special_chars = r"[@$!%*#?&._-+(){}=]"
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter")
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one number")
        if not any(char in valid_special_chars for char in value):
            raise ValueError(
                f"Password must contain at least one special character ({valid_special_chars})"
            )
        if " " in value:
            raise ValueError("Password must not contain spaces")
        return value


class AuthUser(BaseModel):
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
