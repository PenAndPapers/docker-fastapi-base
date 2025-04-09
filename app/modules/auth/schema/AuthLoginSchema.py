from pydantic import BaseModel
from .AuthBaseSchema import AuthBase, AuthUserResponse
from .AuthTokenSchema import TokenResponse


class LoginResponseBasic(BaseModel):
    id: int
    uuid: str

    model_config = {"from_attributes": True}

class LoginRequest(AuthBase):
    pass  # All fields inherited from AuthBase


class LoginResponse(AuthUserResponse):
    token: TokenResponse | None = None  # Only provided after OTP verification
