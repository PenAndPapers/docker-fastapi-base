from sqlalchemy.orm import Session
from typing import List, Optional
from ..model import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, _user: User) -> User:
        pass

    def get_all(self) -> List[User]:
        pass

    def get_by_id(self, id: int) -> Optional[User]:
        pass

    def update(self, _user: User) -> User:
        pass

    def delete(self, _user: User) -> bool:
        pass
