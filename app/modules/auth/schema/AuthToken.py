from pydantic import BaseModel
from datetime import datetime


class AuthToken(BaseModel):
    id: int
    access_token: str


class AuthTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime
