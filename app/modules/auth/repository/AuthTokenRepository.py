from sqlalchemy.orm import Session
from app.database import DatabaseRepository
from ..model import AuthTokenModel
from ..schema import (
    Token,
    TokenRequest,
    TokenResponse,
    TokenUpdateRequest
)


class AuthTokenRepository:
    def __init__(self, db: Session):
        self.db = db
        self.token_repository = DatabaseRepository(db, AuthTokenModel)


    def create(self, data: TokenRequest) -> Token:
        """
        Store user's token
        
        Args:
            data (TokenRequest): Token data

        Returns:
            Token: Token data
        """
        token = self.token_repository.create(data)
        return Token.model_validate(token)


    def get(self, filter_dict: dict) -> Token:
        """
        Get user's token by filter
        
        Args:
            filter_dict (dict): Filter dictionary

        Returns:
            Token: Token data
        """
        token = self.token_repository.get_by_filter(filter_dict)
        return Token.model_validate(token)


    def update(self, data: TokenUpdateRequest) -> TokenResponse:
        """
        Update user's token
        
        Args:
            data (TokenUpdateRequest): Token data

        Returns:
            TokenResponse: Token response data
        """
        token = self.token_repository.update(data.id, data)
        return TokenResponse.model_validate(token)


    def delete(self, id: int) -> None:
        """
        Invalidate all existing tokens for a user
        
        Args:
            id (int): User ID

        Returns:
            None
        """
        self.token_repository.delete_by_filter({"user_id": id})
        self.db.flush()