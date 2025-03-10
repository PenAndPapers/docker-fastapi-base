from pydantic import BaseModel
from datetime import datetime
from ..constants import TokenTypeEnum


class TokenRequest(BaseModel):
    user_id: int
    access_token: str
    refresh_token: str
    expires_at: datetime


class TokenResponse(BaseModel):
    user_id: int
    access_token: str
    refresh_token: str
    expires_at: datetime
    token_type: str = TokenTypeEnum.BEARER.value

    model_config = {"from_attributes": True}
