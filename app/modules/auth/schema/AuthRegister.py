from .AuthBase import AuthBase, AuthUser


class AuthRegister(AuthBase):
    first_name: str
    last_name: str


class AuthRegisterResponse(AuthUser):
    pass
