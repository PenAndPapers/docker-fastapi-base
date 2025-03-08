from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from ..repository import AuthRepository
from ..service import AuthService, AuthPolicy


def get_auth_repository(db: Session = Depends(get_db)) -> AuthRepository:
    return AuthRepository(db)


def get_auth_service(
    repository: AuthRepository = Depends(get_auth_repository),
    policy: AuthPolicy = Depends(),
) -> AuthService:
    return AuthService(repository, policy)
