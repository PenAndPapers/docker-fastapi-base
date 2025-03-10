from .AuthBase import AuthBase, AuthUserResponse


class LoginRequest(AuthBase):
    pass


class LoginResponse(AuthUserResponse):
    pass
