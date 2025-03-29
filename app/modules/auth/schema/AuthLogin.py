from datetime import datetime
from pydantic import BaseModel, Field
from .AuthBase import AuthBase, AuthUserResponse
from .AuthToken import TokenResponse


class LoginVerificationResponse(BaseModel):
    verification_id: str
    expires_at: datetime
    verification_type: str
    temporary_token: str  # For subsequent OTP verification request


class LoginRequest(AuthBase):
    pass  # All fields inherited from AuthBase


class VerifyLoginRequest(AuthBase):
    access_token: str = Field(
        min_length=15,
        max_length=255,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        description="Access token from verification email",
    )
    verification_code: str = Field(
        min_length=1,
        max_length=6,
        example="123456",
        description="Verification code from verification email",
    )
    device_id: str = Field(
        min_length=1,
        max_length=255,
        example="d4f16c9a-0fb6-4a8b-a67e-46c11e51e8b1",
        description="Unique device identifier",
    )
    client_info: str = Field(
        min_length=1,
        max_length=255,
        example="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        description="Client browser/app information",
    )

    model_config = {"from_attributes": True}


class LoginResponse(AuthUserResponse):
    token: TokenResponse | None = None  # Only provided after OTP verification
    requires_verification: bool = True
