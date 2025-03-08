from datetime import datetime
from pydantic import BaseModel, EmailStr, field_validator


class AuthBase(BaseModel):
    email: EmailStr
    password: str

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


class AuthToken(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime


class AuthUser(AuthBase):
    id: int
    first_name: str
    last_name: str
    is_verified: bool
    token: AuthToken
    created_at: datetime
    updated_at: datetime
