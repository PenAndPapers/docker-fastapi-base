from pydantic import BaseModel, Field, EmailStr
from .AuthBase import AuthBase
from .AuthToken import TokenResponse
from passlib.context import CryptContext


class RegisterRequest(AuthBase):
    first_name: str = Field(min_length=1, max_length=75, example="John")
    last_name: str = Field(min_length=1, max_length=75, example="Doe")

    def with_hashed_password(self, pwd_context: CryptContext) -> "RegisterRequest":
        return self.model_copy(update={"password": pwd_context.hash(self.password)})

    model_config = {"from_attributes": True}


class RegisterResponseBasic(BaseModel):
    id: int
    email: EmailStr

    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    email: EmailStr
    token: TokenResponse

    model_config = {"from_attributes": True}
