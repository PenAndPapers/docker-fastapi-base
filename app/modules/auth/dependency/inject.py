from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from ..policy import AuthIPRateLimitingPolicy, AuthMFAPolicy, AuthTokenPolicy
from ..repository import AuthRepository
from ..service import (
    AuthDeviceService,
    AuthLoginService,
    AuthLogoutService,
    AuthOneTimePinService,
    AuthRegisterService,
    AuthTokenService
)


def get_auth_policies():
    """Factory for auth policies"""
    return {
        "ip_rate_limiting_policy": AuthIPRateLimitingPolicy(),
        "mfa_policy": AuthMFAPolicy(),
        "token_policy": AuthTokenPolicy(),
    }


def get_auth_repository(db: Session = Depends(get_db)) -> AuthRepository:
    return AuthRepository(db)


def get_auth_device_service(
    repository: AuthRepository = Depends(get_auth_repository),
) -> AuthDeviceService:
    return AuthDeviceService(repository)


def get_auth_login_service(
    repository: AuthRepository = Depends(get_auth_repository),
) -> AuthLoginService:
    return AuthLoginService(repository)


def get_auth_logout_service(
    repository: AuthRepository = Depends(get_auth_repository),
) -> AuthLogoutService:
    return AuthLogoutService(repository)


def get_auth_one_time_pin_service(
    repository: AuthRepository = Depends(get_auth_repository),
) -> AuthOneTimePinService:
    return AuthOneTimePinService(repository)


def get_auth_register_service(
    repository: AuthRepository = Depends(get_auth_repository),
) -> AuthRegisterService:
    return AuthRegisterService(repository)


def get_auth_token_service(
    repository: AuthRepository = Depends(get_auth_repository),
) -> AuthTokenService:
    return AuthTokenService(repository)
