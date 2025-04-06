from fastapi import HTTPException, status
from app.core import UnauthorizedError
from ..constants import VerificationTypeEnum
from ..repository import AuthRepository
from ..schema import (
    DeviceInfo,
    LoginRequest,
    LoginResponse,
    TokenRequest,
    TokenResponse
)
from .AuthDeviceService import AuthDeviceService
from .AuthTokenService import AuthTokenService
from .AuthOneTimePinService import AuthOneTimePinService


class AuthLoginService:
    def __init__(self, repository: AuthRepository):
        self.repository = repository
        self.device_service = AuthDeviceService(repository)
        self.token_service = AuthTokenService(repository)
        self.otp_service = AuthOneTimePinService(repository)

    def login(self, data: LoginRequest) -> TokenResponse:
        """Login"""
        auth_user = self.repository.login(data)

        if auth_user:
            device_info = DeviceInfo(
                device_id=data.device_id,
                client_info=data.client_info,
            )
            stored_device = self.device_service.handle_store_device(auth_user.id, device_info)

            # We set to False as user need to verifiy their email
            stored_token = self.token_service.store_token(auth_user.id, False)

            user = LoginResponse(
                **auth_user.model_dump(),
                token=stored_token,
                requires_verification=True,
            )

            self.repository.store_verification_code(
                user, VerificationTypeEnum.EMAIL_LOGIN, stored_device.id
            )

            return user

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login failed",
        )