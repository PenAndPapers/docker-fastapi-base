import secrets
from hashlib import sha256
from datetime import datetime, timezone, timedelta
from time import time
from fastapi import HTTPException, status
from ..constants import VerificationTypeEnum
from ..schema import (
    AuthUserResponse,
    DeviceInfo,
    RegisterRequest,
    TokenResponse,
    VerificationRequest,
)
from .AuthTokenService import AuthTokenService


class AuthRegisterService:
    def __init__(self):
        self.token_service = AuthTokenService()

    def register(self, data: RegisterRequest) -> AuthUserResponse:
        """Register"""
        # Keep device info for later use
        device_info = DeviceInfo(
            device_id=data.device_id,
            client_info=data.client_info,
        )

        # Hash the password and send complete data to repository
        hashed_data = data.with_hashed_password(self.pwd_context)

        # Register user (repository will handle field filtering)
        user = self.repository.register(hashed_data)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Register failed",
            )

        stored_device = self._handle_device(user.id, device_info)

        # We set to False as user need to verifiy their email
        stored_token = self._handle_token(user.id, user.email, False)

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
                type=VerificationTypeEnum.EMAIL_SIGNUP,
                attempts=0,
                expires_at=datetime.now(timezone.utc) + timedelta(minutes=55),
                updated_at=datetime.now(timezone.utc),
                verified_at=None,
            )
        )

        self.send_register_email_verification()

        return AuthUserResponse(
            email=user.email,
            token=TokenResponse(**vars(stored_token)),
        )


    def send_register_email_verification(self) -> None:
      # TODO: send verification code to user's email/sms
      pass