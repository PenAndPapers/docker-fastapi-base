from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.core import UnauthorizedError, logger
from ..constants import TokenTypeEnum
from ..repository import AuthRepository
from ..policy import AuthTokenPolicy, AuthIPRateLimitingPolicy, AuthMFAPolicy
from ..schema import (
    DeviceInfo,
    DeviceRequest,
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    TokenRequest,
    TokenResponse,
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
        logger.info(f"User registered: {auth_user}")

        if auth_user:
            self._handle_device(auth_user.id, device_info)
            stored_token = self._handle_token(auth_user.id)

            return RegisterResponse(
                **auth_user.model_dump(),
                token=stored_token,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Register failed",
        )

    def login(self, data: LoginRequest) -> LoginResponse:
        """Login"""
        auth_user = self.repository.login(data)

        if auth_user:
            device_info = DeviceInfo(
                device_id=data.device_id,
                client_info=data.client_info,
            )
            self._handle_device(auth_user.id, device_info)
            stored_token = self._handle_token(auth_user.id)

            return LoginResponse(
                **auth_user.model_dump(),
                token=stored_token,
                varification=None,
                requires_verification=False,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login failed",
        )

    def logout(self, data: LogoutRequest) -> LogoutResponse:
        """Logout"""
        return self.repository.logout(data)

    def refresh_token(self, data: TokenRequest) -> TokenResponse:
        """Refresh token and generate new access token"""
        # Verify access token refresh eligibility first
        self.token_policy.verify_token_refresh_eligibility(data.access_token)

        # Only if eligible, verify refresh token
        user_id_from_token = self.token_policy._verify_token(
            data.refresh_token, token_type=TokenTypeEnum.REFRESH
        )

        # Ensure token belongs to the requesting user
        if int(user_id_from_token) != data.user_id:
            raise UnauthorizedError(detail="Token does not belong to the user")

        return self._handle_token(data.user_id)

    def _handle_token(self, user_id: int) -> TokenResponse:
        """Handle user token generation and storage"""

        # Invalidate existing user tokens
        self.repository.invalidate_user_tokens(user_id)

        # Generate new token for the user
        token_data = self.token_policy._generate_token(user_id)

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

    def _handle_device(self, user_id: int, device: DeviceInfo) -> None:
        """Handle user device information and storage"""

        # Invalidate existing user devices
        self.repository.invalidate_user_devices(user_id)

        # Store device information
        self.repository.store_device(
            DeviceRequest(
                user_id=user_id,
                device_id=device.device_id,
                client_info=device.client_info,
            )
        )
