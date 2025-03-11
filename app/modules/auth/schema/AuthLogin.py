from datetime import datetime
from pydantic import BaseModel, Field, EmailStr
from .AuthBase import AuthBase, AuthUserResponse
from .AuthToken import TokenResponse


class LoginVerificationResponse(BaseModel):
    verification_id: str
    expires_at: datetime
    verification_type: str
    temporary_token: str  # For subsequent OTP verification request


class LoginRequest(AuthBase):
    device_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        example="d4f16c9a-0fb6-4a8b-a67e-46c11e51e8b1",
    )
    client_info: str = Field(
        ...,
        min_length=1,
        max_length=255,
        example="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0",
    )


class LoginResponse(AuthUserResponse):
    token: TokenResponse | None = None  # Only provided after OTP verification
    verification: LoginVerificationResponse | None = None  # For pending verification
    requires_verification: bool = True
