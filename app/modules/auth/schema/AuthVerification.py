from pydantic import BaseModel, Field
from datetime import datetime
from app.modules.auth.constants import VerificationTypeEnum


class VerificationRequest(BaseModel):
    user_id: int
    token_id: int
    device_id: int
    code: str = Field(
        min_length=6,
        max_length=6,
        example="123456",
        description="6-digit verification code",
    )
    type: VerificationTypeEnum
    expires_at: datetime
    is_verified: bool = False
    verified_at: datetime | None = None
    attempts: int = 0

    model_config = {"from_attributes": True}


class VerificationResponse(BaseModel):
    pass
