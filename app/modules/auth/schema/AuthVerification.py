from pydantic import BaseModel, Field
from datetime import datetime
from app.modules.auth.constants import VerificationTypeEnum


class __VerificationBase(BaseModel):
    user_id: int
    token_id: int
    device_id: int
    code: str
    attempts: int
    is_verified: bool
    type: VerificationTypeEnum
    expires_at: datetime
    verified_at: datetime | None = None

    model_config = {"from_attributes": True}


class VerificationRequest(__VerificationBase):
    code: str = Field(
        min_length=6,
        max_length=6,
        example="123456",
        description="6-digit verification code",
    )
    attempts: int = 0

    model_config = {"from_attributes": True}


class VerificationUpdateRequest(BaseModel):
    id: int
    token_id: int
    is_verified: bool = True
    verified_at: datetime | None = None

    model_config = {"from_attributes": True}


class VerificationResponse(__VerificationBase):
    id: int

    model_config = {"from_attributes": True}
