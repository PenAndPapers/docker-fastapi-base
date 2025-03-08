from sqlalchemy.orm import Session
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


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db

    def register(self, data: AuthRegister) -> AuthRegisterResponse:
        print(data)

    def login(self, data: AuthLogin) -> AuthLoginResponse:
        print(data)

    def logout(self, data: AuthLogout) -> AuthLogoutResponse:
        print(data)

    def refresh_token(self, data: AuthToken) -> AuthTokenResponse:
        print(data)
