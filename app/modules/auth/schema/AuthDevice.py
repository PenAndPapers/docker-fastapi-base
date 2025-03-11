from datetime import datetime
from pydantic import BaseModel, Field


class DeviceRequest(BaseModel):
    user_id: int | None = Field(default=None, description="User ID")
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

    model_config = {"from_attributes": True}


class DeviceResponse(BaseModel):
    user_id: int = Field(..., description="User ID")
    device_id: str = Field(..., description="Device identifier")
    client_info: str = Field(..., description="Client information")
    last_login: datetime = Field(..., description="Last login timestamp")

    model_config = {"from_attributes": True}
