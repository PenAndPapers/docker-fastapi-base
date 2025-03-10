import jwt
import uuid
from datetime import datetime, timedelta
from typing import Optional
from fastapi import HTTPException, status
from app.core import app_settings
from ..constants import TokenTypeEnum
from ..schema import TokenResponse


class AuthTokenPolicy:
    def __init__(self, user_repository):
        self.secret_key = app_settings.jwt_secret_key
        self.algorithm = app_settings.jwt_algorithm
        self.access_token_expire_minutes = app_settings.jwt_access_token_expire_minutes
        self.refresh_token_expire_days = app_settings.jwt_refresh_token_expire_days
        self.user_repository = user_repository

    def _generate_token(self, user_id: int) -> TokenResponse:
        # Validate user exists in database
        user = self.user_repository.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        # Generate access and refresh tokens
        access_token_expires = datetime.utcnow() + timedelta(
            minutes=self.access_token_expire_minutes
        )
        refresh_token_expires = datetime.utcnow() + timedelta(
            days=self.refresh_token_expire_days
        )

        access_token = self._create_token(
            data={"sub": str(user_id)}, expires_delta=access_token_expires
        )
        refresh_token = self._create_token(
            data={"sub": str(user_id)}, expires_delta=refresh_token_expires
        )

        return TokenResponse(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=access_token_expires,
            token_type=TokenTypeEnum.BEARER,  # here we manually set the token type as bearer
        )

    def _create_token(self, data: dict, expires_delta: datetime, token_type: TokenTypeEnum = TokenTypeEnum.ACCESS) -> str:
        to_encode = data.copy()
        to_encode.update({
            "exp": expires_delta.timestamp(),
            "iat": datetime.utcnow().timestamp(),
            "nbf": datetime.utcnow().timestamp(),
            "jti": str(uuid.uuid4()),
            "iss": app_settings.app_name,
            "aud": app_settings.app_audience,
            "type": token_type,
        })
        return jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)

    def _verify_token(self, token: str, verify_exp: bool = True, token_type: TokenTypeEnum = TokenTypeEnum.ACCESS) -> str:
        try:
            options = {"verify_exp": verify_exp}
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm], options=options)
            
            # Verify token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type: expected {token_type}"
                )
                
            if not payload.get("sub"):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token: missing subject claim"
                )
            return payload["sub"]
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
