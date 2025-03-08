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

    def register(self, data: AuthRegister) -> AuthRegisterResponse:
        """Register"""
        res = self.policy._generate_token(1)
        print(f"\n\n\n{res}\n\n\n")
        return self.repository.register(data)

    def login(self, data: AuthLogin) -> AuthLoginResponse:
        """Login"""
        return self.repository.login(data)

    def logout(self, data: AuthLogout) -> AuthLogoutResponse:
        """Logout"""
        return self.repository.logout(data)

    def refresh_token(self, data: AuthToken) -> AuthTokenResponse:
        """Refresh"""
        return self.repository.refresh(data)
