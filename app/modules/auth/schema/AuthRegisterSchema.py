from pydantic import BaseModel
from .AuthBaseSchema import AuthBase
from .AuthTokenSchema import TokenResponse
from passlib.context import CryptContext


class RegisterRequest(AuthBase):
    def with_hashed_password(self, pwd_context: CryptContext) -> "RegisterRequest":
        return self.model_copy(update={"password": pwd_context.hash(self.password)})

    model_config = {"from_attributes": True}


class RegisterResponseBasic(BaseModel):
    id: int
    uuid: str

    model_config = {"from_attributes": True}


class RegisterResponse(BaseModel):
    token: TokenResponse

    model_config = {"from_attributes": True}
