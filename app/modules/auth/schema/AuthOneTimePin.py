from pydantic import BaseModel
from .AuthToken import TokenResponse

class OneTimePinRequest(BaseModel):
    access_token: str
    code: str
    device_id: str
    client_info: str

class OneTimePinResponse(BaseModel):
    token: TokenResponse
    message: str