from pydantic import BaseModel, Field
from datetime import datetime
from ..constants import TokenTypeEnum


class Token(BaseModel):
    id: int
    user_id: int
    access_token: str
    refresh_token: str
    expires_at: datetime
    token_type: str = TokenTypeEnum.BEARER.value

    model_config = {"from_attributes": True}


class TokenRequest(BaseModel):
    user_id: int = Field(example=1)
    access_token: str = Field(
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", min_length=300
    )
    refresh_token: str = Field(
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", min_length=300
    )
    expires_at: datetime = Field(example="2024-12-31T23:59:59")
    deleted_at: datetime = Field(example="2024-12-31T23:59:59", default=None)

    model_config = {"from_attributes": True}


class TokenUpdateRequest(BaseModel):
    id: int = Field(example=1)
    deleted_at: datetime = Field(example="2024-12-31T23:59:59", default=None)

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    expires_at: datetime
    token_type: str = TokenTypeEnum.BEARER.value

    model_config = {"from_attributes": True}
