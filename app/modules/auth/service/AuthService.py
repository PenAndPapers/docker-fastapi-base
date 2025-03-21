from datetime import datetime
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
    VerificationRequest,
    VerificationResponse,
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

            user = RegisterResponse(
                **auth_user.model_dump(),
                token=TokenResponse(**vars(stored_token)),
            )

            self.repository.store_verification_code(
                user,
                stored_token.id,
                stored_device.id,
                VerificationTypeEnum.EMAIL_SIGNUP,
            )

            # TODO: Send verification code to user's email/sms

            return user

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Register failed",
        )
        """Logout"""
        return self.repository.logout(data)

    def one_time_pin(self, data: OneTimePinRequest) -> TokenResponse:
        """Verify registration using tokens sent via email/sms"""
        # First decode and verify the access token to get user info
        try:
            payload = self.token_policy._verify_token(
                data.access_token, 
                token_type=TokenTypeEnum.ACCESS
            )
            user_id = int(payload)  # payload contains the user_id from sub claim
        except UnauthorizedError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid access token"
            )

        # Check if verification code exists and is valid
        verification = self.repository.get_verification_code(
            user_id, 
            data.verification_code
        )
        if not verification:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

        # Validate attempts and expiration
        if verification.attempts >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Too many attempts"
            )

        if datetime.utcnow() > verification.expires_at:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code expired"
            )

        # Mark verification as complete
        verification.is_verified = True
        verification.verified_at = datetime.utcnow()
        self.repository.update_verification_code(verification)

        # Generate new token with verified status
        user = self.repository.get_user(user_id)  # You'll need to add this method
        new_token = self._handle_token(user_id, user.email, True)

        return TokenResponse(**vars(new_token))

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

    def _handle_token(self, user_id: int, user_email: str, is_token_verified: bool = False) -> Token:
        """Handle user token generation and storage"""

        # Invalidate existing user tokens
        self.repository.invalidate_user_tokens(user_id)

        # Generate new token for the user
        token_data = self.token_policy._generate_token(user_id, user_email, is_token_verified)

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
