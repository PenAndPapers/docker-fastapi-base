from datetime import datetime, timezone, timedelta
from fastapi import HTTPException, status
from app.core import UnauthorizedError
from ..constants import TokenTypeEnum, VerificationTypeEnum
from ..schema import (
    AuthUserResponse,
    OneTimePinRequest,
    TokenUpdateRequest,
    TokenResponse,
    VerificationUpdateRequest,
)
from app.modules.user.schema import UserUpdateRequest
from app.modules.user.constants import UserStatusEnum


class AuthOneTimePinService:

    def one_time_pin(self, data: OneTimePinRequest) -> AuthUserResponse:
        """Verify user's one-time-pin"""
        try:
            payload = self.token_policy._verify_token(
                data.access_token, token_type=TokenTypeEnum.ACCESS
            )
            user_id = int(payload["sub"])  # Extract and convert to integer
        except (UnauthorizedError, ValueError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid access token"
            )

        # Get user info
        user = self.repository.get_user(user_id)

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
        new_token = self._handle_token(user_id, user.email, data.access_token, True)

        # Update user's email verification status
        if new_token and verification.type == VerificationTypeEnum.EMAIL_SIGNUP:
            user = UserUpdateRequest(
                **vars(user),
                is_verified=True,
                status=UserStatusEnum.ACTIVE,
                verified_at=current_time,
                updated_at=current_time,
            )

            print("\n\n\n\n", user, "\n\n\n\n")
            # Update user verified_at field
            self.repository.update_user(user)

        # Return with required fields
        return AuthUserResponse(
            email=user.email,
            token=TokenResponse(**vars(new_token))
        )