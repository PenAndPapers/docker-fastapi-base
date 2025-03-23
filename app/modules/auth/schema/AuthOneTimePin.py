from pydantic import BaseModel, Field
from .AuthToken import TokenResponse


class OneTimePinRequest(BaseModel):
    access_token: str = Field(..., min_length=15)
    verification_code: str = Field(..., min_length=6, max_length=6)
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


class OneTimePinResponse(BaseModel):
    token: TokenResponse
    message: str
