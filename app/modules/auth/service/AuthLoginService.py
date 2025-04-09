import secrets
from hashlib import sha256
from datetime import datetime, timezone, timedelta
from time import time
from fastapi import HTTPException, status
from ..constants import VerificationTypeEnum
from ..repository import AuthRepository
from ..schema import (
    AuthUserResponse,
    DeviceInfo,
    LoginRequest,
    TokenResponse,
    VerificationRequest
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

    def login(self, data: LoginRequest) -> AuthUserResponse:
        """Login"""
        user = self.repository.login(data)

        if user:
            device_info = DeviceInfo(
                device_id=data.device_id,
                client_info=data.client_info,
            )
            stored_device = self.device_service.store_device(user.id, device_info)

            # We set to False as user need to verifiy their email
            stored_token = self.token_service.store_token(user.id, user.uuid, False)

            # Generate a unique seed using user ID, token, timestamp and a random nonce
            nonce = secrets.token_hex(16)  # Add extra randomness
            seed = f"{user.id}-{stored_token.access_token}-{int(time())}-{nonce}"

            # Generate hash and ensure 6 unique digits
            hash_bytes = sha256(seed.encode()).digest()
            num = int.from_bytes(hash_bytes, byteorder="big")

            self.repository.store_verification_code(
                VerificationRequest(
                    user_id=user.id,
                    token_id=stored_token.id,
                    device_id=stored_device.id,
                    code=format(int(str(num)[-6:]), "06d"),  # Ensure exactly 6 digits
                    type=VerificationTypeEnum.EMAIL_LOGIN,
                    attempts=0,
                    expires_at=datetime.now(timezone.utc) + timedelta(minutes=55),
                    updated_at=datetime.now(timezone.utc),
                    verified_at=None,
                )
            )

            self.send_login_email_verification()

            return AuthUserResponse(
                token=TokenResponse(**vars(stored_token)),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login failed",
        )


    def send_login_email_verification(self) -> None:
        pass