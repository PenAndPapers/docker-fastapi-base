from .AuthBase import AuthBase, AuthUser
from .AuthToken import AuthTokenResponse
from passlib.context import CryptContext


class AuthRegister(AuthBase):
    first_name: str
    last_name: str

    def with_hashed_password(self, pwd_context: CryptContext) -> "AuthRegister":
        return self.model_copy(update={"password": pwd_context.hash(self.password)})

    model_config = {"from_attributes": True}


class AuthRegisterResponse(AuthUser):
    token: AuthTokenResponse

    model_config = {"from_attributes": True}
