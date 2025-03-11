from fastapi import HTTPException, status
from passlib.context import CryptContext
from app.core import UnauthorizedError
from ..constants import TokenTypeEnum
from ..repository import AuthRepository
from ..policy import AuthTokenPolicy, AuthIPRateLimitingPolicy, AuthMFAPolicy
from ..schema import (
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
        device_info = {"device_id": data.device_id, "client_info": data.client_info}

        # Hash the password and send complete data to repository
        hashed_data = data.with_hashed_password(self.pwd_context)

        # Register user (repository will handle field filtering)
        auth_user = self.repository.register(hashed_data)

        if auth_user:
            # Generate token and store it
            token_data = self.token_policy._generate_token(auth_user.id)
            stored_token = self.repository.store_token(
                TokenRequest(
                    user_id=auth_user.id,
                    access_token=token_data.access_token,
                    refresh_token=token_data.refresh_token,
                    expires_at=token_data.expires_at,
                )
            )

            # Store device information
            self.repository.store_device(
                DeviceRequest(
                    user_id=auth_user.id,
                    device_id=device_info["device_id"],
                    client_info=device_info["client_info"],
                )
            )

            stored_token.token_type = token_data.token_type
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
        user = self.repository.login(data)
        print(f"\n\n\n\n{user}\n\n\n\n")

    def logout(self, data: LogoutRequest) -> LogoutResponse:
        """Logout"""
        return self.repository.logout(data)

    def refresh_token(self, data: TokenRequest) -> TokenResponse:
        """Refresh token and generate new access token"""
        # 1. Verify access token refresh eligibility first
        self.token_policy.verify_token_refresh_eligibility(data.access_token)

        # 2. Only if eligible, verify refresh token
        user_id_from_token = self.token_policy._verify_token(
            data.refresh_token, token_type=TokenTypeEnum.REFRESH
        )

        # 3. Ensure token belongs to the requesting user
        if int(user_id_from_token) != data.user_id:
            raise UnauthorizedError(detail="Token does not belong to the user")

        # 3. Invalidate old tokens
        self.repository.invalidate_user_tokens(data.user_id)

        # 4. Generate new token pair
        new_tokens = self.token_policy._generate_token(data.user_id)

        # 5. Store the new tokens in database
        stored_token = self.repository.store_token(
            TokenRequest(
                user_id=data.user_id,
                access_token=new_tokens.access_token,
                refresh_token=new_tokens.refresh_token,
                expires_at=new_tokens.expires_at,
            )
        )

        stored_token.token_type = new_tokens.token_type
        return stored_token
