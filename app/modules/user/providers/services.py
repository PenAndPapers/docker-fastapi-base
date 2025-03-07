from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from ..repository import UserRepository
from ..service import UserService, UserPolicy


def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_user_service(
    repository: UserRepository = Depends(get_user_repository),
    policy: UserPolicy = Depends(),
) -> UserService:
    return UserService(repository, policy)
