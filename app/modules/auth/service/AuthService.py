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
            generated_token = TokenResponse.model_validate(
                self.token_policy._generate_token(auth_user.id)
            )
            stored_token = self.repository.store_token(
                generated_token.model_dump(exclude={"token_type"})
            )

            return RegisterResponse(
                **auth_user.model_dump(),
                token=TokenResponse(
                    **stored_token, token_type=generated_token.token_type
                ),
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
        """Refresh"""
        return self.repository.refresh(data)
