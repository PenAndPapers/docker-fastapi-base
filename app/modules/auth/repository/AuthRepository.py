from sqlalchemy.orm import Session
from ..model import AuthDevice, AuthToken, AuthVerification
from ..schema import (
    AuthUserResponse,
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    TokenRequest,
    TokenResponse,
)
from app.database import DatabaseRepository
from app.modules.user.model import User


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = DatabaseRepository(db, User)
        self.token_repository = DatabaseRepository(db, AuthToken)

    def register(self, data: RegisterRequest) -> AuthUserResponse:
        """Register a user"""
        user = self.user_repository.create(data)
        return AuthUserResponse(
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

    def login(self, data: LoginRequest) -> LoginResponse:
        """Login a user"""
        print(data)
        pass

    def logout(self, data: LogoutRequest) -> LogoutResponse:
        """Logout a user"""
        print(data)
        pass

    def store_token(self, data: TokenRequest) -> TokenResponse:
        """Store a new token for a user"""
        token = self.token_repository.create(data)
        return TokenResponse(**vars(token))

    def invalidate_user_tokens(self, user_id: int) -> None:
        """Invalidate all existing tokens for a user"""
        self.token_repository.delete_by_filter({"user_id": user_id})
