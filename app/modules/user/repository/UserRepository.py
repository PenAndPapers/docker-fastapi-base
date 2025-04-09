from sqlalchemy.orm import Session
from ..model import UserModel


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, _user: UserModel):
        pass

    def get_all(self):
        pass

    def get_by_id(self, id: int):
        pass

    def update(self, _user: UserModel):
        pass

    def delete(self, _user: UserModel):
        pass
