from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.core import UnauthorizedError
from app.database import DatabaseRepository
from app.modules.user.model import UserModel
from app.modules.user.schema import UserCreateRequest, UserUpdateRequest, UserResponse
from ..model import AuthDeviceModel, AuthTokenModel, AuthOneTimePinModel
from ..schema import (
    DeviceRequest,
    DeviceResponse,
    RegisterRequest,
    RegisterResponseBasic,
    LoginResponseBasic,
    LoginRequest,
    LogoutRequest,
    LogoutResponse,
    Token,
    TokenRequest,
    TokenResponse,
    TokenUpdateRequest,
    OneTimePinRequest,
    OneTimePinUpdateRequest,
    OneTimePinResponse,
)


class AuthRepository:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = DatabaseRepository(db, UserModel)
        self.device_repository = DatabaseRepository(db, AuthDeviceModel)
        self.token_repository = DatabaseRepository(db, AuthTokenModel)
        self.one_time_pin_repository = DatabaseRepository(db, AuthOneTimePinModel)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def register(self, data: RegisterRequest) -> RegisterResponseBasic:
        """Register a user"""
        # Filter and convert to UserCreateRequest
        user_data = data.model_dump(exclude={"device_id", "client_info"})
        user_request = UserCreateRequest(**user_data)

        # Create user with filtered data
        user = self.user_repository.create(user_request)

        return RegisterResponseBasic(id=user.id, uuid=user.uuid)

    def update_user(self, data: UserUpdateRequest) -> UserResponse:
        """Update user"""
        user = self.user_repository.update(data.id, data)
        return UserResponse.model_validate(user)

    def login(self, data: LoginRequest) -> LoginResponseBasic:
        """Verify user credentials"""
        # Use direct column comparison instead of dict
        user = (
            self.db.query(UserModel)
            .filter(
                UserModel.email == data.email,
                UserModel.deleted_at.is_(None),  # Check if account is not deleted
                UserModel.verified_at.is_not(None),  # Check if account is verified
            )
            .first()
        )

        # Check if user exists and password is correct
        if not user or not self.pwd_context.verify(data.password, user.password):
            raise UnauthorizedError(detail="Invalid credentials")

        return LoginResponseBasic(id=user.id, uuid=user.uuid,)

    def logout(self, data: LogoutRequest) -> LogoutResponse:
        """Logout a user"""
        # TODO: Implement
        pass

    def store_token(self, data: TokenRequest) -> Token:
        """Store a new token for a user"""
        token = self.token_repository.create(data)
        return Token.model_validate(token)

    def get_token(self, filter_dict: dict) -> Token:
        """Get a token by access token"""
        token = self.token_repository.get_by_filter(filter_dict)
        return Token.model_validate(token)

    def update_token(self, data: TokenUpdateRequest) -> TokenResponse:
        """Update a token"""
        token = self.token_repository.update(data.id, data)
        return TokenResponse.model_validate(token)

    def invalidate_user_tokens(self, user_id: int) -> None:
        """Invalidate all existing tokens for a user"""
        self.token_repository.delete_by_filter({"user_id": user_id})
        self.db.flush()

    def store_device(self, data: DeviceRequest) -> DeviceResponse:
        """Store device info"""
        device = self.device_repository.create(data)
        return DeviceResponse.model_validate(device)

    def invalidate_user_devices(self, user_id: int) -> None:
        """Invalidate all existing devices for a user"""
        self.device_repository.delete_by_filter({"user_id": user_id})
        self.db.flush()

    def store_one_time_pin_code(
        self,
        one_time_pin_data: OneTimePinRequest
    ) -> OneTimePinResponse:
        """Store verification code"""
        one_time_pin = self.one_time_pin_repository.create(one_time_pin_data)
        return OneTimePinResponse(**vars(one_time_pin))

    def get_one_time_pin_code(
        self, filter_dict: dict
    ) -> OneTimePinResponse:
        """Get verification code and increment attempt counter"""
        one_time_pin = self.one_time_pin_repository.get_by_filter(filter_dict)

        if one_time_pin:
            # Convert SQLAlchemy model to dict, then to VerificationResponse
            return OneTimePinResponse(**vars(one_time_pin))

        return None

    def update_verification_code(
        self, verification: OneTimePinUpdateRequest
    ) -> OneTimePinResponse:
        """Update verification code"""
        updated_verification = self.verification_repository.update(
            verification.id, verification
        )

        return OneTimePinResponse(**vars(updated_verification))

    def invalidate_verification_code(self) -> None:
        """Invalidate verification code"""
        # TODO: Implement
        pass

    def get_user(self, user_id: int) -> UserResponse:
        """Get user by ID"""
        user = self.user_repository.get_one(user_id)
        return UserResponse(**vars(user))

    def get_user_by_filter(self, filter_dict: dict) -> UserResponse:
        """Get user by filter"""
        user = self.user_repository.get_by_filter(filter_dict)
        return UserResponse(**vars(user)) if user else None
