from pydantic import Field, EmailStr
from .AuthBase import AuthBase, AuthUserResponse
from .AuthToken import TokenResponse
from passlib.context import CryptContext


class RegisterRequest(AuthBase):
    first_name: str = Field(min_length=1, max_length=75, example="John")
    last_name: str = Field(min_length=1, max_length=75, example="Doe")

    def with_hashed_password(self, pwd_context: CryptContext) -> "RegisterRequest":
        return self.model_copy(update={"password": pwd_context.hash(self.password)})

    model_config = {"from_attributes": True}


class RegisterResponse(AuthUserResponse):
    token: TokenResponse

    model_config = {"from_attributes": True}
