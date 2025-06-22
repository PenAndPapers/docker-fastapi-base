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


    def logout(self):
        """Logout a user"""
        # TODO: Implement
        pass


    def get(self, id: int) -> UserResponse:
        """
        Get user by ID

        Args:
            id (int): User ID

        Returns:
            UserResponse: User response data
        """
        user = self.user_repository.get_one(id)
        return UserResponse(**vars(user))


    def get_by_filter(self, filter_dict: dict) -> UserResponse:
        """
        Get user by filter
        
        Args:
            filter_dict (dict): Filter dictionary

        Returns:
            UserResponse: User data
        """
        return UserResponse(**vars(user))


    def update(self, data: UserUpdateRequest) -> UserResponse:
        """
        Update user
        
        Args:
            data (UserUpdateRequest): User data

        Returns:
            UserResponse: User data
        """
        user = self.user_repository.update(data.id, data)
        return UserResponse.model_validate(user)
