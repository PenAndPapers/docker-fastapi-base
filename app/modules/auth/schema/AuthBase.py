from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator
from app.modules.user.schema.UserBase import UserBase


class AuthBase(BaseModel):
    email: EmailStr = Field(
        example="johndoe.test@email.com", description="Valid email address"
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=72,
        example="P@ssw0rd123",
        description="Password must contain uppercase, lowercase, number, and special character",
    )

    model_config = {"from_attributes": True}

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        valid_special_chars = r"[@$!%*#?&._-+(){}=]"

        validation_rules = [
            (
                lambda password: any(char.isupper() for char in password),
                "Password must contain at least one uppercase letter",
            ),
            (
                lambda password: any(char.islower() for char in password),
                "Password must contain at least one lowercase letter",
            ),
            (
                lambda password: any(char.isalpha() for char in password),
                "Password must contain at least one letter",
            ),
            (
                lambda password: any(char.isdigit() for char in password),
                "Password must contain at least one number",
            ),
            (
                lambda password: any(char in valid_special_chars for char in password),
                f"Password must contain at least one special character ({valid_special_chars})",
            ),
            (lambda password: " " not in password, "Password must not contain spaces"),
        ]

        for validator, error_message in validation_rules:
            if not validator(value):
                raise ValueError(error_message)

        return value


class AuthUserResponse(UserBase):
    pass
