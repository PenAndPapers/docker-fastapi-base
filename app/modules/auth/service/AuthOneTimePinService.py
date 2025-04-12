from datetime import datetime, timezone
from app.core import BadRequestError, UnauthorizedError
from app.modules.user.constants import UserStatusEnum
from app.modules.user.schema import UserResponse, UserUpdateRequest
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
            token = self.token_policy._verify_token(
                data.access_token, token_type=TokenTypeEnum.ACCESS
            )

            uuid = token["sub"]
        except (UnauthorizedError, ValueError):
            raise BadRequestError("Invalid access token")

        # Get user
        user = self.repository.get_user_by_filter({ "uuid": uuid, "deleted_at": None })
        
        if not user:
            raise BadRequestError("User not found")

        # Check if verification code exists and is valid
        verification = self.repository.get_verification_code({
            "user_id": user.id,
            "code": data.verification_code,
            "deleted_at": None
        })
        current_time = datetime.now(timezone.utc)

        # Validate verification code if valid/exists
        if not verification:
            raise BadRequestError("Invalid verification code")

        # Make the comparison using timezone-aware datetimes
        if current_time > verification.expires_at:
            # TODO update verification deleted_at field make it soft delete
            raise BadRequestError("Verification code expired")

        # Validate attempts and expiration
        if verification.attempts >= 3:
            raise BadRequestError("Too many attempts")

        attempts = verification.attempts + 1

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
            self.verify_new_user(user)

        # Return with required fields
        return AuthUserResponse(
            token=TokenResponse(**vars(new_token))
        )


    def verify_new_user(self, user: UserResponse):
        """Set new user account as verified account"""
        current_time = datetime.now(timezone.utc)

        user_dict = user.model_dump()
        user_dict["is_verified"] = True
        user_dict["status"] = UserStatusEnum.ACTIVE
        user_dict["verified_at"] = current_time
        user_dict["updated_at"] = current_time

        user = UserUpdateRequest(**user_dict)

        # Update user verified_at field
        self.repository.update_user(user)