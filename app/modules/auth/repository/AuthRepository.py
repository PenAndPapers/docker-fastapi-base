from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.core import UnauthorizedError
from ..model import AuthDevice, AuthToken, AuthVerification
from ..schema import (
    AuthUserResponse,
    DeviceRequest,
    DeviceResponse,
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    TokenRequest,
    TokenResponse,
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

    def register(self, data: RegisterRequest) -> AuthUserResponse:
        """Register a user"""
        # Filter and convert to UserCreateRequest
        user_data = data.model_dump(exclude={"device_id", "client_info"})
        user_request = UserCreateRequest(**user_data)

        # Create user with filtered data
        user = self.user_repository.create(user_request)

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

    def login(self, data: LoginRequest) -> LoginResponse:
        """Verify user credentials"""
        # Use direct column comparison instead of dict
        user = self.db.query(User).filter(User.email == data.email).first()

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
        print(data)
        pass

    def store_token(self, data: TokenRequest) -> TokenResponse:
        """Store a new token for a user"""
        token = self.token_repository.create(data)
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
