from datetime import datetime
from typing import TypedDict
from pydantic import BaseModel, Field


class DeviceFilter(TypedDict, total = False):
    user_id: int | None
    device_id: str | None
    client_info: str | None
    last_login: datetime | None
    created_at: datetime | None
    updated_at: datetime | None
    deleted_at: datetime | None


class DeviceInfo(BaseModel):
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


class DeviceRequest(DeviceInfo):
  user_id: int | None = Field(default=None, description="User ID")

  model_config = {"from_attributes": True}


class DeviceResponse(BaseModel):
    id: int = Field(..., description="Device ID")
    user_id: int = Field(..., description="User ID")
    device_id: str = Field(..., description="Device identifier")
    client_info: str = Field(..., description="Client information")
    last_login: datetime = Field(..., description="Last login timestamp")

    model_config = {"from_attributes": True}

