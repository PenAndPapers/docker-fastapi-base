from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.core import UnauthorizedError
from app.modules.user.schema import UserUpdateRequest
from app.modules.user.constants import UserStatusEnum
from ..constants import TokenTypeEnum, VerificationTypeEnum
from ..schema import (
    AuthUserResponse,
    OneTimePinRequest,
    TokenUpdateRequest,
    TokenResponse,
    VerificationUpdateRequest,
)
from ..repository import AuthRepository
from ..policy import AuthTokenPolicy
from .AuthTokenService import AuthTokenService


class AuthOneTimePinService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository
        self.token_policy = AuthTokenPolicy()
        self.token_service = AuthTokenService(repository)

    def one_time_pin(self, data: OneTimePinRequest) -> AuthUserResponse:
        """Verify user's one-time-pin"""
        try:
            payload = self.token_policy._verify_token(
                data.access_token, token_type=TokenTypeEnum.ACCESS
            )

            print("\n\n\n\n", payload, "\n\n\n\n")

            uuid = payload["sub"]  # Extract and convert to integer
        except (UnauthorizedError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access token"
            )

        # Get user
        user = self.repository.get_user_by_filter({ "uuid": uuid, "deleted_at": None })

        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User not found",
            )

        # Check if verification code exists and is valid
        verification = self.repository.get_verification_code({
            "user_id": user.id,
            "code": data.verification_code,
            "deleted_at": None
        })

        # Validate verification code if valid/exists
        if not verification:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid verification code",
            )

        # Make the comparison using timezone-aware datetimes
        if datetime.now(timezone.utc) > verification.expires_at:
            # TODO update verification deleted_at field make it soft delete
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Verification code expired",
            )

        # Validate attempts and expiration
        if verification.attempts >= 3:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Too many attempts"
            )

        attempts = verification.attempts + 1
        current_time = datetime.now(timezone.utc)

        # Get the user's current token
        current_token = self.repository.get_token({
            "user_id": user.id,
            "access_token": data.access_token,
            "deleted_at": None
        })

        # Update verification code
        # Make old verification code inactive and soft delete it
        self.repository.update_verification_code(
            VerificationUpdateRequest(
                id=verification.id,
                attempts=attempts,
                verified_at=current_time,
                updated_at=current_time,
                deleted_at=current_time
            )
        )

        # Make old token inactive and soft delete it
        self.repository.update_token(
            TokenUpdateRequest(
                id=current_token.id,
                is_active=False,
                updated_at=current_time,
                deleted_at=current_time,
            )
        )

        # Generate new token with verified status
        new_token = self.token_service.store_token(user.id, user.uuid, data.access_token, True)

        # Update user's email verification status
        if new_token and verification.type == VerificationTypeEnum.EMAIL_SIGNUP:
            user_dict = user.model_dump()
            user_dict.pop("is_verified", None)
            user_dict.pop("status", None)
            user_dict.pop("verified_at", None)
            user_dict.pop("updated_at", None)
            user = UserUpdateRequest(
                **user_dict,
                is_verified=True,
                status=UserStatusEnum.ACTIVE,
                verified_at=current_time,
                updated_at=current_time,
            )

            # Update user verified_at field
            self.repository.update_user(user)

        # Return with required fields
        return AuthUserResponse(
            token=TokenResponse(**vars(new_token))
        )