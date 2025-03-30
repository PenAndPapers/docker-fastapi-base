import secrets
from hashlib import sha256
from datetime import datetime, timezone, timedelta
from time import time
from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.core import UnauthorizedError
from ..constants import TokenTypeEnum, VerificationTypeEnum
from ..repository import AuthRepository
from ..policy import AuthTokenPolicy, AuthIPRateLimitingPolicy, AuthMFAPolicy
from ..schema import (
    AuthUserResponse,
    DeviceInfo,
    DeviceRequest,
    DeviceResponse,
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    OneTimePinRequest,
    Token,
    TokenRequest,
    TokenUpdateRequest,
    TokenResponse,
    VerificationRequest,
    VerificationUpdateRequest,
)


class AuthService:
    def __init__(
        self,
        repository: AuthRepository,
        token_policy: AuthTokenPolicy,
        ip_rate_limiting_policy: AuthIPRateLimitingPolicy = None,
        mfa_policy: AuthMFAPolicy = None,
    ):
        self.repository = repository
        self.token_policy = token_policy
        self.ip_policy = ip_rate_limiting_policy
        self.mfa_policy = mfa_policy
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=14
        )

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

        # TODO: Send verification code to user's email/sms

        return AuthUserResponse(
            email=user.email,
            token=TokenResponse(**vars(stored_token)),
        )

    def one_time_pin(self, data: OneTimePinRequest) -> AuthUserResponse:
        """Verify user's one-time-pin"""
        try:
            payload = self.token_policy._verify_token(
                data.access_token, token_type=TokenTypeEnum.ACCESS
            )
            user_id = int(payload["sub"])  # Extract and convert to integer
        except (UnauthorizedError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access token"
            )

        # Get user info
        user = self.repository.get_user(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )

        # Check if verification code exists and is valid
        verification = self.repository.get_verification_code({
            "user_id": user.id,
            "code": data.verification_code,
            "deleted_at": None
        })

        # Validate verification code if valid/exists
        if not verification:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code",
            )

        # Make the comparison using timezone-aware datetimes
        if datetime.now(timezone.utc) > verification.expires_at:
            # TODO update verification deleted_at field make it soft delete
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code expired",
            )

        # Validate attempts and expiration
        if verification.attempts >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Too many attempts"
            )

        attempts = verification.attempts + 1
        current_time = datetime.now(timezone.utc)

        # Get the user's current token
        current_token = self.repository.get_token({
            "user_id": user.id,
            "access_token": data.access_token,
            "deleted_at": None
        })

        # Update verification code
        # Make old verification code inactive and soft delete it
        self.repository.update_verification_code(
            VerificationUpdateRequest(
                id=verification.id,
                attempts=attempts,
                verified_at=current_time,
                updated_at=current_time,
                deleted_at=current_time
            )
        )

        # Make old token inactive and soft delete it
        self.repository.update_token(
            TokenUpdateRequest(
                id=current_token.id,
                is_active=False,
                updated_at=current_time,
                deleted_at=current_time,
            )
        )

        # Generate new token with verified status
        new_token = self._handle_token(user_id, user.email, data.access_token, True)

        # Return with required fields
        return AuthUserResponse(
            email=user.email,
            token=TokenResponse(**vars(new_token))
        )

    def login(self, data: LoginRequest) -> AuthUserResponse:
        """Login"""
        auth_user = self.repository.login(data)

        if auth_user:
            device_info = DeviceInfo(
                device_id=data.device_id,
                client_info=data.client_info,
            )
            stored_device = self._handle_device(auth_user.id, device_info)

            # We set to False as user need to verifiy their email
            stored_token = self._handle_token(auth_user.id, False)

            user = LoginResponse(
                **auth_user.model_dump(),
                token=stored_token,
                requires_verification=True,
            )

            self.store_verification_code(
                user, VerificationTypeEnum.EMAIL_LOGIN, stored_device.id
            )

            return user

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login failed",
        )

    def logout(self, data: LogoutRequest) -> LogoutResponse:
        """Logout"""
        pass

    def refresh_token(self, data: TokenRequest) -> TokenResponse:
        """Refresh token and generate new access token"""
        # Verify access token refresh eligibility first
        self.token_policy._verify_token_refresh_eligibility(data.access_token)

        # Only if eligible, verify refresh token
        user_id_from_token = self.token_policy._verify_token(
            data.refresh_token, token_type=TokenTypeEnum.REFRESH
        )

        # Ensure token belongs to the requesting user
        if int(user_id_from_token) != data.user_id:
            raise UnauthorizedError(detail="Token does not belong to the user")

        return self._handle_token(data.user_id)

    def _handle_token(
        self, user_id: int, user_email: str, access_token: str, is_token_verified: bool = False
    ) -> Token:
        """Handle user token generation and storage"""

        # Generate new token for the user
        token_data = self.token_policy._generate_token(
            user_id, user_email, is_token_verified
        )

        # Store user token
        stored_token = self.repository.store_token(
            TokenRequest(
                user_id=user_id,
                access_token=token_data.access_token,
                refresh_token=token_data.refresh_token,
                expires_at=token_data.expires_at,
            )
        )

        # Update token type
        stored_token.token_type = token_data.token_type

        return stored_token

    def _handle_device(self, user_id: int, device: DeviceInfo) -> DeviceResponse:
        """Handle user device information and storage"""

        # Store device information
        stored_device = self.repository.store_device(
            DeviceRequest(
                user_id=user_id,
                device_id=device.device_id,
                client_info=device.client_info,
            )
        )

        return stored_device
