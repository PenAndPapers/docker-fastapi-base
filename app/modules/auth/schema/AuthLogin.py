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
    pass  # All fields inherited from AuthBase


class LoginResponse(AuthUserResponse):
    token: TokenResponse | None = None  # Only provided after OTP verification
    verification: LoginVerificationResponse | None = None  # For pending verification
    requires_verification: bool = True
