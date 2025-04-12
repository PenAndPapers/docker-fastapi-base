from app.core import UnauthorizedError
from ..constants import TokenTypeEnum
from ..schema import (
    Token,
    TokenRequest,
    TokenResponse,
)
from ..repository import AuthRepository
from ..policy import AuthTokenPolicy

class AuthTokenService:
    def __init__(
        self,
        repository: AuthRepository
    ):
        self.repository = repository
        self.token_policy = AuthTokenPolicy()

    def refresh_token(self, data: TokenRequest) -> TokenResponse:
        """Refresh token and generate new access token"""
        # Verify access token refresh eligibility first
        self.token_policy._verify_token_refresh_eligibility(data.access_token)

        # Only if eligible, verify refresh token
        user_id_from_token = self.token_policy._verify_token(
            data.refresh_token, token_type=TokenTypeEnum.REFRESH
        )

        # Ensure token belongs to the requesting user
        if int(user_id_from_token) != data.user_id:
            raise UnauthorizedError(detail="Token does not belong to the user")

        return self.store_token(data.user_id)

    def store_token(
        self, user_id: int, uuid: str, is_token_verified: bool = False
    ) -> Token:
        """Handle user token generation and storage"""

        # Generate new token for the user
        token_data = self.token_policy._generate_token(
            uuid, is_token_verified
        )

        # Store user token
        stored_token = self.repository.store_token(
            TokenRequest(
                user_id=user_id,
                access_token=token_data.access_token,
                refresh_token=token_data.refresh_token,
                expires_at=token_data.expires_at,
            )
        )

        # Update token type
        stored_token.token_type = token_data.token_type

        return stored_token
