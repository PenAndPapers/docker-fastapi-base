from pydantic import BaseModel, Field, EmailStr
from .AuthTokenSchema import TokenResponse


class OneTimePinRequest(BaseModel):
    access_token: str = Field(
        ..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", min_length=300
    )
    verification_code: str = Field(..., example="123456", min_length=6, max_length=6)
    device_id: str = Field(
        ...,
        min_length=1,
        max_length=255,
        example="d4f16c9a-0fb6-4a8b-a67e-46c11e51e8b1",
        description="Unique device identifier",
    )
    client_info: str = Field(
        ...,
        min_length=1,
        max_length=255,
        example="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
        description="Client browser/app information",
    )


class OneTimePinUpdateRequest(BaseModel):
    id: int
    attempts: int
    updated_at: datetime
    verified_at: datetime | None = None
    deleted_at: datetime | None = None

    model_config = {"from_attributes": True}


class OneTimePinResponse(BaseModel):
    email: EmailStr
    token: TokenResponse

    model_config = { "from_attributes": True }
