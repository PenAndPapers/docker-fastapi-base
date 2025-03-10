from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from ..repository import AuthRepository
from ..service import AuthService, AuthTokenPolicy


def get_auth_repository(db: Session = Depends(get_db)) -> AuthRepository:
    return AuthRepository(db)


def get_auth_service(
    repository: AuthRepository = Depends(get_auth_repository),
    token_policy: AuthTokenPolicy = Depends(),
) -> AuthService:
    return AuthService(repository, token_policy)
