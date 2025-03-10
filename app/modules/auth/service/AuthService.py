from fastapi import HTTPException, status
from passlib.context import CryptContext
from .AuthTokenPolicy import AuthTokenPolicy
from ..repository.AuthRepository import AuthRepository
from ..schema import (
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
    def __init__(self, repository: AuthRepository, token_policy: AuthTokenPolicy):
        self.repository = repository
        self.token_policy = token_policy
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=14
        )

    def register(self, data: RegisterRequest) -> RegisterResponse:
        """Register"""
        auth_user = self.repository.register(
            data.with_hashed_password(self.pwd_context)
        )

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

            # Override the default token_type with the one from policy
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
        return self.repository.login(data)

    def logout(self, data: LogoutRequest) -> LogoutResponse:
        """Logout"""
        return self.repository.logout(data)

    def refresh_token(self, data: TokenRequest) -> TokenResponse:
        """Refresh token and generate new access token"""
        # 1. Verify tokens belong to the claimed user
        user_id_from_token = self.token_policy._verify_token(
            data.refresh_token,
            token_type=TokenTypeEnum.REFRESH
        )
        
        # 2. Ensure token belongs to the requesting user
        if int(user_id_from_token) != data.user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token does not belong to the user"
            )

        # 3. Generate new token pair
        new_tokens = self.token_policy._generate_token(data.user_id)
        
        # 4. Store the new tokens in database
        stored_token = self.repository.store_token(TokenRequest(
            user_id=data.user_id,
            access_token=new_tokens.access_token,
            refresh_token=new_tokens.refresh_token,
            expires_at=new_tokens.expires_at,
        ))

        stored_token.token_type = new_tokens.token_type
        return stored_token
