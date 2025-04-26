import secrets
from hashlib import sha256
from datetime import datetime, timezone, timedelta
from time import time
from passlib.context import CryptContext
from app.core import BadRequestError
from ..constants import OneTimePinTypeEnum
from ..schema import (
    AuthUserResponse,
    DeviceInfo,
    RegisterRequest,
    TokenResponse,
    VerificationRequest,
)
from ..repository import AuthDeviceRepository, AuthOneTimePinRepository, AuthTokenRepository, AuthUserRepository
from .AuthDeviceService import AuthDeviceService
from .AuthTokenService import AuthTokenService


class AuthRegisterService:
    def __init__(
        self,
        device_repository: AuthDeviceRepository,
        one_time_pin_repository: AuthOneTimePinRepository,
        token_repository: AuthTokenRepository,
        user_repository: AuthUserRepository,
    ):
        self.device_service = AuthDeviceService(device_repository)
        self.token_service = AuthTokenService(token_repository)
        self.one_time_pin_repository = one_time_pin_repository
        self.user_repository = user_repository
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=14
        )

    def register(self, data: RegisterRequest) -> AuthUserResponse:
        """Register"""
        
        # Hash the password and send complete data to repository
        hashed_data = data.with_hashed_password(self.pwd_context)

        # Register user (repository will handle field filtering)
        user = self.user_repository.register(hashed_data)

        if not user:
            raise BadRequestError(detail="Register failed")

        # Keep device info for later use
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
        now = datetime.now(timezone.utc)

        self.one_time_pin_repository.store_one_time_pin(
            VerificationRequest(
                user_id=user.id,
                token_id=stored_token.id,
                device_id=stored_device.id,
                code=format(int(str(num)[-6:]), "06d"),  # Ensure exactly 6 digits
                type=OneTimePinTypeEnum.EMAIL_SIGNUP,
                attempts=0,
                expires_at=now + timedelta(minutes=55),
                updated_at=now,
                verified_at=None,
            )
        )

        self.send_register_email_verification()

        return AuthUserResponse(
            token=TokenResponse(**vars(stored_token)),
        )


    def send_register_email_verification(self) -> None:
      # TODO: send verification code to user's email/sms
      pass