from datetime import datetime, timezone
from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.core import UnauthorizedError
from ..constants import TokenTypeEnum, VerificationTypeEnum
from ..repository import AuthRepository
from ..policy import AuthTokenPolicy, AuthIPRateLimitingPolicy, AuthMFAPolicy
from ..schema import (
    DeviceInfo,
    DeviceRequest,
    DeviceResponse,
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    OneTimePinRequest,
    OneTimePinResponse,
    Token,
    TokenRequest,
    TokenResponse,
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

    def register(self, data: RegisterRequest) -> RegisterResponse:
        """Register"""
        # Keep device info for later use
        device_info = DeviceInfo(
            device_id=data.device_id,
            client_info=data.client_info,
        )

        # Hash the password and send complete data to repository
        hashed_data = data.with_hashed_password(self.pwd_context)

        # Register user (repository will handle field filtering)
        auth_user = self.repository.register(hashed_data)

        if auth_user:
            stored_device = self._handle_device(auth_user.id, device_info)

            # We set to False as user need to verifiy their email
            stored_token = self._handle_token(auth_user.id, auth_user.email, False)

            self.repository.store_verification_code(
                auth_user.id,
                stored_device.id,
                stored_token.id,
                stored_token.access_token,
                VerificationTypeEnum.EMAIL_SIGNUP,
            )

            # TODO: Send verification code to user's email/sms

            return RegisterResponse(
                email=auth_user.email,
                token=TokenResponse(**vars(stored_token)),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Register failed",
        )

    def one_time_pin(self, data: OneTimePinRequest) -> OneTimePinResponse:
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

        # Check if verification code exists and is valid
        verification = self.repository.get_verification_code(
            user_id, data.verification_code
        )

        # Validate verification code if valid/exists
        if not verification:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code",
            )

        # Update attempts
        update_data = VerificationUpdateRequest(
            id=verification.id,
            token_id=verification.token_id,
            attempts=verification.attempts + 1,
            updated_at=datetime.now(timezone.utc),
        )
        self.repository.update_verification_code(update_data)

        # Validate attempts and expiration
        if verification.attempts >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Too many attempts"
            )

        # Make the comparison using timezone-aware datetimes
        if datetime.now(timezone.utc) > verification.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code expired",
            )

        # Generate new token with verified status
        new_token = self._handle_token(user_id, user.email, True)

        # Mark verification as complete
        current_time = datetime.now(timezone.utc)
        update_data = VerificationUpdateRequest(
            id=verification.id, is_verified=True, verified_at=current_time
        )
        self.repository.update_verification_code(update_data)

        # Return with required fields
        return OneTimePinResponse(
            email=user.email,
            token=TokenResponse(**vars(new_token)),
            message="Email verification successful",
        )

    def login(self, data: LoginRequest) -> LoginResponse:
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
        self, user_id: int, user_email: str, is_token_verified: bool = False
    ) -> Token:
        """Handle user token generation and storage"""

        # Invalidate existing user tokens
        self.repository.invalidate_user_tokens(user_id)

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

        # Invalidate existing user devices
        self.repository.invalidate_user_devices(user_id)

        # Store device information
        stored_device = self.repository.store_device(
            DeviceRequest(
                user_id=user_id,
                device_id=device.device_id,
                client_info=device.client_info,
            )
        )

        return stored_device
