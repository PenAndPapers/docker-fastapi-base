from fastapi import HTTPException, status
from passlib.context import CryptContext
from .AuthPolicy import AuthPolicy
from ..repository.AuthRepository import AuthRepository
from ..schema import (
    AuthRegister,
    AuthRegisterResponse,
    AuthLogin,
    AuthLoginResponse,
    AuthLogout,
    AuthLogoutResponse,
    AuthToken,
    AuthTokenResponse,
)


class AuthService:
    def __init__(self, repository: AuthRepository, policy: AuthPolicy):
        self.repository = repository
        self.policy = policy
        self.pwd_context = CryptContext(
            schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=14
        )

    def register(self, data: AuthRegister) -> AuthRegisterResponse:
        """Register"""
        auth_user = self.repository.register(
            data.with_hashed_password(self.pwd_context)
        )

        if auth_user:
            token = self.policy._generate_token(auth_user.id)
            self.repository.store_token(token)

            return AuthRegisterResponse(
                **auth_user.model_dump(),
                token=AuthTokenResponse(
                    access_token=token.access_token,
                    refresh_token=token.refresh_token,
                    expires_at=token.expires_at,
                ),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Register failed",
        )

    def login(self, data: AuthLogin) -> AuthLoginResponse:
        """Login"""
        return self.repository.login(data)

    def logout(self, data: AuthLogout) -> AuthLogoutResponse:
        """Logout"""
        return self.repository.logout(data)

    def refresh_token(self, data: AuthToken) -> AuthTokenResponse:
        """Refresh"""
        return self.repository.refresh(data)
