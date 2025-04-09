from pydantic import BaseModel, EmailStr, Field, field_validator
from .AuthTokenSchema import TokenResponse


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
    device_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        example="d4f16c9a-0fb6-4a8b-a67e-46c11e51e8b1",
        description="Unique device identifier",
    )
    client_info: str = Field(
        ...,
        min_length=1,
        max_length=255,
        example="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        description="Client browser/app information",
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


class AuthUserResponse(BaseModel):
    email: EmailStr
    token: TokenResponse
