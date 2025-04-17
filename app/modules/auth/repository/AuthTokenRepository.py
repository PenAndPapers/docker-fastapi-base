from sqlalchemy.orm import Session
from app.database import DatabaseRepository
from ..model import AuthTokenModel
from ..schema import (
    Token,
    TokenRequest,
    TokenResponse,
    TokenUpdateRequest
)


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db
        self.token_repository = DatabaseRepository(db, AuthTokenModel)

    def store_token(self, data: TokenRequest) -> Token:
        """Store a new token for a user"""
        token = self.token_repository.create(data)
        return Token.model_validate(token)

    def get_token(self, filter_dict: dict) -> Token:
        """Get a token by access token"""
        token = self.token_repository.get_by_filter(filter_dict)
        return Token.model_validate(token)

    def update_token(self, data: TokenUpdateRequest) -> TokenResponse:
        """Update a token"""
        token = self.token_repository.update(data.id, data)
        return TokenResponse.model_validate(token)

    def invalidate_user_tokens(self, user_id: int) -> None:
        """Invalidate all existing tokens for a user"""
        self.token_repository.delete_by_filter({"user_id": user_id})
        self.db.flush()