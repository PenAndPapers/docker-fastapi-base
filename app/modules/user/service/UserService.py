from typing import List
from ..repository.UserRepository import UserRepository
from ..model import User
from ..schema import UserCreate, UserUpdate
from .UserPolicy import UserPolicy


class UserService:
    def __init__(self, repository: UserRepository, policy: UserPolicy):
        self.repository = repository
        self.policy = policy

    def create(self, data: UserCreate) -> User:
        """Create a new record."""
        return self.repository.create(data)

    def get_all(self) -> List[User]:
        """Get all record."""
        return self.repository.get_all()

    def get_by_id(self, id: int) -> User:
        """Get a record by its ID."""
        return self.repository.get_by_id(id)

    def update(self, id: int, data: UserUpdate) -> User:
        """Update a record by its ID."""
        self.get_by_id(id)
        return self.repository.update(id, data)

    def delete(self, id: int) -> bool:
        """Delete a record by its ID."""
        self.get_by_id(id)
        return self.repository.delete(id)
