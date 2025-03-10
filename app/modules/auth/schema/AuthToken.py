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

    model_config = {
        "from_attributes": True,
        "json_schema_extra": {
            "example": {
                "user_id": 1,
                "access_token": "some_random_strings",
                "refresh_token": "some_random_strings",
                "expires_at": "2023-08-01T00:00:00",
                "token_type": "bearer",
            }
        },
    }
