from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from ..policy import AuthIPRateLimitingPolicy, AuthMFAPolicy, AuthTokenPolicy
from ..repository import AuthRepository
from ..service import AuthService  # Remove duplicate AuthTokenPolicy import


def get_auth_repository(db: Session = Depends(get_db)) -> AuthRepository:
    return AuthRepository(db)


def get_auth_policies():
    """Factory for auth policies"""
    return {
        "ip_rate_limiting_policy": AuthIPRateLimitingPolicy(),
        "mfa_policy": AuthMFAPolicy(),
        "token_policy": AuthTokenPolicy(),
    }


def get_auth_service(
    repository: AuthRepository = Depends(get_auth_repository),
) -> AuthService:
    policies = get_auth_policies()
    return AuthService(repository=repository, **policies)
