import secrets
from hashlib import sha256
from time import time
from datetime import datetime, timezone, timedelta
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.core import UnauthorizedError
from ..constants import VerificationTypeEnum
from ..model import AuthDevice, AuthToken, AuthVerification
from ..schema import (
    AuthUserResponse,
    DeviceRequest,
    DeviceResponse,
    RegisterRequest,
    RegisterResponseBasic,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    Token,
    TokenRequest,
    TokenResponse,
    VerificationRequest,
    VerificationUpdateRequest,
    VerificationResponse,
)
from app.database import DatabaseRepository
from app.modules.user.model import User
from app.modules.user.schema import UserCreateRequest


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = DatabaseRepository(db, User)
        self.token_repository = DatabaseRepository(db, AuthToken)
        self.device_repository = DatabaseRepository(db, AuthDevice)
        self.verification_repository = DatabaseRepository(db, AuthVerification)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def register(self, data: RegisterRequest) -> RegisterResponseBasic:
        """Register a user"""
        # Filter and convert to UserCreateRequest
        user_data = data.model_dump(exclude={"device_id", "client_info"})
        user_request = UserCreateRequest(**user_data)

        # Create user with filtered data
        user = self.user_repository.create(user_request)

        return RegisterResponseBasic(id=user.id, email=user.email)

    def login(self, data: LoginRequest) -> LoginResponse:
        """Verify user credentials"""
        # Use direct column comparison instead of dict
        user = (
            self.db.query(User)
            .filter(
                User.email == data.email,
                User.deleted_at.is_(None),  # Check if account is not deleted
                User.is_verified.is_(True),  # Check if account is verified
            )
            .first()
        )

        if not user or not self.pwd_context.verify(data.password, user.password):
            raise UnauthorizedError(detail="Invalid credentials")

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

    def logout(self, data: LogoutRequest) -> LogoutResponse:
        """Logout a user"""
        # TODO: Implement
        pass

    def store_token(self, data: TokenRequest) -> Token:
        """Store a new token for a user"""
        token = self.token_repository.create(data)
        return Token(**vars(token))

    def get_token(self, access_token: str) -> TokenResponse:
        """Get a token by access token"""
        token = self.token_repository.get_by_filter({"access_token": access_token})
        return TokenResponse(**vars(token))

    def invalidate_user_tokens(self, user_id: int) -> None:
        """Invalidate all existing tokens for a user"""
        self.token_repository.delete_by_filter({"user_id": user_id})
        self.db.flush()

    def store_device(self, data: DeviceRequest) -> DeviceResponse:
        """Store device info"""
        device = self.device_repository.create(data)
        return DeviceResponse(**vars(device))

    def invalidate_user_devices(self, user_id: int) -> None:
        """Invalidate all existing devices for a user"""
        self.device_repository.delete_by_filter({"user_id": user_id})
        self.db.flush()

    def store_verification_code(
        self,
        user_id: int,
        device_id: int,
        token_id: int,
        access_token: str,
        type: VerificationTypeEnum,
    ) -> VerificationResponse:
        """Store verification code"""
        # Generate a unique seed using user ID, token, timestamp and a random nonce
        nonce = secrets.token_hex(16)  # Add extra randomness
        seed = f"{user_id}-{access_token}-{int(time())}-{nonce}"

        # Generate hash and ensure 6 unique digits
        hash_bytes = sha256(seed.encode()).digest()
        num = int.from_bytes(hash_bytes, byteorder="big")

        # Ensure exactly 6 digits
        verification_code = format(int(str(num)[-6:]), "06d")

        verification_data = VerificationRequest(
            user_id=user_id,
            token_id=token_id,
            device_id=device_id,
            code=verification_code,
            type=type,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=55),
            attempts=0,
            is_verified=False,
            verified_at=None,
        )

        verification = self.verification_repository.create(verification_data)
        return VerificationResponse(**vars(verification))

    def get_verification_code(
        self, user_id: int, verification_code: str
    ) -> VerificationResponse:
        """Get verification code and increment attempt counter"""
        verification = self.verification_repository.get_by_filter(
            {"user_id": user_id, "code": verification_code, "is_verified": False}
        )

        if verification:
            # Convert SQLAlchemy model to dict, then to VerificationResponse
            return VerificationResponse(**vars(verification))

        return None

    def update_verification_code(
        self, verification: VerificationUpdateRequest
    ) -> VerificationResponse:
        """Update verification code"""
        updated_verification = self.verification_repository.update(
            verification.id, verification
        )

        return VerificationResponse(**vars(updated_verification))

    def invalidate_verification_code(self) -> None:
        """Invalidate verification code"""
        # TODO: Implement
        pass

    def get_user(self, user_id: int) -> AuthUserResponse:
        """Get user by ID"""
        user = self.user_repository.get_one(user_id)
        return AuthUserResponse(**vars(user))
