from pydantic import BaseModel
from datetime import datetime


class AuthToken(BaseModel):
    user_id: int
    access_token: str
    refresh_token: str
    expires_at: datetime


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime

    class Config:
        from_attributes = True
