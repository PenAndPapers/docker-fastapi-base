from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.core import UnauthorizedError
from app.database import DatabaseRepository
from app.modules.user.model import UserModel
from app.modules.user.schema import UserCreateRequest, UserUpdateRequest, UserResponse
from ..schema import (
    RegisterRequest,
    RegisterResponseBasic,
    LoginResponseBasic,
    LoginRequest,
    LogoutRequest,
    LogoutResponse,
)


class AuthUserRepository:
    def __init__(self, db: Session):
        self.db = db
        self.user_repository = DatabaseRepository(db, UserModel)
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def register(self, data: RegisterRequest) -> RegisterResponseBasic:
        """Register a user"""
        # Filter and convert to UserCreateRequest
        user_data = data.model_dump(exclude={"device_id", "client_info"})
        user_request = UserCreateRequest(**user_data)

        # Create user with filtered data
        user = self.user_repository.create(user_request)

        return RegisterResponseBasic(id=user.id, uuid=user.uuid)

    def login(self, data: LoginRequest) -> LoginResponseBasic:
        """Verify user credentials and return user basic information
        
        Args:
            data (LoginRequest): Login request data containing email and password

        Returns:
            LoginResponseBasic: User basic information

        Raises:
            UnauthorizedError: If user does not exist or email/password is incorrect
        """
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

    def get_user(self, user_id: int) -> UserResponse:
        """Get user by ID"""
        user = self.user_repository.get_one(user_id)
        return UserResponse(**vars(user)) if user else None

    def get_user_by_filter(self, filter_dict: dict) -> UserResponse:
        """Get user by filter"""
        user = self.user_repository.get_by_filter(filter_dict)
        return UserResponse(**vars(user)) if user else None

    def update_user(self, data: UserUpdateRequest) -> UserResponse:
        """Update user"""
        user = self.user_repository.update(data.id, data)
        return UserResponse.model_validate(user) if user else None
