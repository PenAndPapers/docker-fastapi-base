from datetime import datetime, timedelta
from typing import Optional
import jwt
import uuid
from fastapi import HTTPException, status
from app.core import app_settings
from ..schema import AuthToken


class AuthPolicy:
    SECRET_KEY = app_settings.jwt_secret_key
    ALGORITHM = app_settings.jwt_algorithm
    ACCESS_TOKEN_EXPIRE_MINUTES = app_settings.jwt_access_token_expire_minutes
    REFRESH_TOKEN_EXPIRE_DAYS = app_settings.jwt_refresh_token_expire_days

    def _generate_token(self, user_id: int) -> AuthToken:
        access_token_expires = datetime.utcnow() + timedelta(
            minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        refresh_token_expires = datetime.utcnow() + timedelta(
            days=self.REFRESH_TOKEN_EXPIRE_DAYS
        )

        access_token = self._create_token(
            data={"sub": str(user_id)}, expires_delta=access_token_expires
        )
        refresh_token = self._create_token(
            data={"sub": str(user_id)}, expires_delta=refresh_token_expires
        )

        return AuthToken(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=access_token_expires,
        )

    def _create_token(self, data: dict, expires_delta: datetime) -> str:
        to_encode = data.copy()
        # Add more claims for security
        to_encode.update(
            {
                "exp": expires_delta.timestamp(),
                "iat": datetime.utcnow().timestamp(),  # issued at
                "jti": str(uuid.uuid4()),  # unique token ID
                "type": "access",  # or "refresh" for refresh tokens
            }
        )
        return jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)

    def _verify_token(self, token: str) -> Optional[str]:
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            return payload.get("sub")
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )
