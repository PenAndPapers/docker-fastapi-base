from sqlalchemy.orm import Session
from ..schema import (
    AuthUser,
    AuthRegister,
    AuthLogin,
    AuthLoginResponse,
    AuthLogout,
    AuthLogoutResponse,
    AuthToken,
    AuthTokenResponse,
)
from app.database import DatabaseRepository
from app.modules.user.model import User, UserToken


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = DatabaseRepository(db, User)
        self.token_repository = DatabaseRepository(db, UserToken)

    def register(self, data: AuthRegister) -> AuthUser:
        user = self.user_repository.create(data)
        return AuthUser(
            id=user.id,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            phone_number=user.phone_number,
            gender=user.gender,
            date_of_birth=user.date_of_birth,
            address=user.address,
            is_verified=user.is_verified,
            created_at=user.created_at,
            updated_at=user.updated_at,
            deleted_at=user.deleted_at,
        )

    def login(self, data: AuthLogin) -> AuthLoginResponse:
        print(data)

    def logout(self, data: AuthLogout) -> AuthLogoutResponse:
        print(data)

    def store_token(self, data: AuthToken) -> AuthTokenResponse:
        return self.token_repository.create(data)

    def refresh_token(self, user_id: int, data: AuthToken) -> AuthTokenResponse:
        print(data)
