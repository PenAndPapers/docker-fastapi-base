from pydantic import BaseModel, Field
from datetime import datetime
from app.modules.auth.constants import OneTimePinTypeEnum


class __VerificationBase(BaseModel):
    user_id: int = Field(
        ...,
        description="User ID",
        example=1,
    )
    token_id: int = Field(
        ...,
        description="Token ID",
        example=1,
    )
    device_id: int = Field(
       ...,
        description="Device ID",
        example=1,
    )
    code: str = Field(
        min_length=6,
        max_length=6,
        example="123456",
        description="6-digit verification code",
    )
    attempts: int = Field(
        default=0,
        description="Number of attempts",
        example=0,
    )
    type: OneTimePinTypeEnum
    expires_at: datetime
    verified_at: datetime | None = None
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}


class VerificationRequest(__VerificationBase):
    code: str = Field(
        min_length=6,
        max_length=6,
        example="123456",
        description="6-digit verification code",
    )

    model_config = {"from_attributes": True}


class VerificationUpdateRequest(BaseModel):
    id: int
    attempts: int
    updated_at: datetime
    verified_at: datetime | None = None
    deleted_at: datetime | None = None
    model_config = {"from_attributes": True}


class VerificationResponse(__VerificationBase):
    id: int

    model_config = {"from_attributes": True}
