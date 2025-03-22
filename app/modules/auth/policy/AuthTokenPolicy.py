import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from app.core import app_settings, UnauthorizedError
from ..constants import TokenTypeEnum
from ..schema import TokenResponse


class AuthTokenPolicy:
    def __init__(self):  # Remove user_repository parameter
        self.secret_key = app_settings.jwt_secret_key
        self.algorithm = app_settings.jwt_algorithm
        self.access_token_expire_minutes = app_settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = app_settings.jwt_refresh_token_expire_days

    def _raise_token_error(self, detail: str) -> None:
        """Raise a standardized token validation error"""
        raise UnauthorizedError(detail=detail)

    def _generate_token(
        self, user_id: int, is_token_verified: bool = False
    ) -> TokenResponse:
        access_token_expires = datetime.utcnow() + timedelta(
            minutes=self.access_token_expire_minutes
        )
        refresh_token_expires = datetime.utcnow() + timedelta(
            days=self.refresh_token_expire_days
        )

        access_token = self._create_token(
            data={"sub": str(user_id), "verified": is_token_verified},
            expires_delta=access_token_expires,
            token_type=TokenTypeEnum.ACCESS,  # Explicitly set token type
        )
        refresh_token = self._create_token(
            data={"sub": str(user_id), "verified": is_token_verified},
            expires_delta=refresh_token_expires,
            token_type=TokenTypeEnum.REFRESH,  # Explicitly set token type
        )

        return TokenResponse(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=access_token_expires,
            token_type=TokenTypeEnum.BEARER,  # here we manually set the token type as bearer
        )

    def _create_token(
        self,
        data: dict,
        expires_delta: datetime,
        token_type: TokenTypeEnum = TokenTypeEnum.ACCESS,
    ) -> str:
        to_encode = data.copy()
        to_encode.update(
            {
                "exp": expires_delta.timestamp(),
                "iat": datetime.utcnow().timestamp(),
                "nbf": datetime.utcnow().timestamp(),
                "jti": str(uuid.uuid4()),
                "iss": app_settings.app_name,
                "aud": app_settings.app_audience,
                "type": token_type,
            }
        )
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def _verify_token(
        self,
        token: str,
        verify_exp: bool = True,
        token_type: TokenTypeEnum = TokenTypeEnum.ACCESS,
    ) -> str:
        try:
            # First decode without verification to check token structure
            unverified_payload = jwt.decode(token, options={"verify_signature": False})

            # Then do full verification with our requirements
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_exp": verify_exp,
                    "verify_signature": True,
                    "verify_aud": True,
                    "verify_iat": True,
                    "verify_nbf": True,
                },
                audience=app_settings.app_audience,
            )

            # Verify token type
            token_type_in_payload = payload.get("type")
            if not token_type_in_payload:
                self._raise_token_error("Token type missing")

            if token_type_in_payload != token_type:
                self._raise_token_error(
                    f"Invalid token type: expected {token_type}, got {token_type_in_payload}"
                )

            # Verify subject claim
            subject = payload.get("sub")
            if not subject:
                self._raise_token_error("Invalid token: missing subject claim")

            return subject

        except jwt.ExpiredSignatureError:
            self._raise_token_error("Token has expired")
        except jwt.InvalidAudienceError:
            self._raise_token_error(
                f"Invalid token audience: expected {app_settings.app_audience}"
            )
        except jwt.InvalidTokenError as e:
            self._raise_token_error(f"Invalid token: {str(e)}")

    def _verify_token_refresh_eligibility(self, access_token: str) -> None:
        """
        Verifies if the access token is eligible for refresh (>75% of lifetime elapsed)
        Raises UnauthorizedError if token is not eligible for refresh
        """
        try:
            token_exp_percentage = self._get_token_expiry_percentage(access_token)
            if token_exp_percentage < 75:
                raise UnauthorizedError(
                    detail="Access token is not close enough to expiry for refresh"
                )
        except jwt.InvalidTokenError:
            pass  # Continue if access token is invalid/expired

    def _get_token_expiry_percentage(self, token: str) -> float:
        """Calculate what percentage of the token's lifetime has elapsed"""
        payload = jwt.decode(token, options={"verify_signature": False})
        exp = payload.get("exp")
        iat = payload.get("iat")

        if not (exp and iat):
            return 100

        now = datetime.utcnow().timestamp()
        total_lifetime = exp - iat
        time_elapsed = now - iat

        return (time_elapsed / total_lifetime) * 100
