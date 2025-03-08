from pydantic import BaseModel


class AuthLogout(BaseModel):
    id: int
    access_token: str


class AuthLogoutResponse(BaseModel):
    message: str
