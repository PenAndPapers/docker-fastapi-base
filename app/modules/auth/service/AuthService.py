from datetime import datetime
from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.core import UnauthorizedError
from ..constants import TokenTypeEnum. VerificationTypeEnum
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
    VerificationRequest,
    VerificationResponse
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
            stored_token = self._handle_token(auth_user.id, False)

            user = RegisterResponse(
                **auth_user.model_dump(),
                token=stored_token,
            )

            self.repository.store_verification_code(user, VerificationTypeEnum.EMAIL_SIGNUP, stored_device.id)

            return user

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
            stored_device = self._handle_device(auth_user.id, device_info)

            # We set to False as user need to verifiy their email
            stored_token = self._handle_token(auth_user.id, False)

            user = LoginResponse(
                **auth_user.model_dump(),
                token=stored_token,
                requires_verification=True,
            )

            self.store_verification_code(user, VerificationTypeEnum.EMAIL_LOGIN, stored_device.id)

            return user

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Login failed",
        )

    def logout(self, data: LogoutRequest) -> LogoutResponse:
        """Logout"""
        return self.repository.logout(data)

    def one_time_pin(self, data: VerificationRequest) -> RegisterResponse:
        """Verify registration using tokens sent via email/sms"""

         # check if verification code exists
        verification = self.repository.get_verification_code(data.user_id, data.verification_code)
        if not verification:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

        if verification.attempts >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Too many attempts"
            )

        # check if verification code is associated with access token and user
        token = self.repository.get_token(data.access_token)
        if not token or not(token.user_id == data.user_id and verification.access_token == data.access_token):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

        # check if code already expired
        now = datetime.utcnow().timestamp()
        expires_at = verification.expires_at.timestamp()
        is_expired = now > expires_at
        if is_expired:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code"
            )

        # TODO
        # 1. Get verification code from database using the token
        # 2. Verify code that is valid
        # 3. Verify code that is not expired
        # 4. Verify code is associated with user id and access token
        # 5. Update user status to verified
        # 6. Invalidate all existing tokens for the user
            
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

    def _handle_token(self, user_id: int, is_token_verified: bool = False) -> TokenResponse:
        """Handle user token generation and storage"""

        # Invalidate existing user tokens
        self.repository.invalidate_user_tokens(user_id)

        # Generate new token for the user
        token_data = self.token_policy._generate_token(user_id, is_token_verified)

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
