from pydantic import BaseModel


class LogoutRequest(BaseModel):
    id: int
    access_token: str


class LogoutResponse(BaseModel):
    message: str
