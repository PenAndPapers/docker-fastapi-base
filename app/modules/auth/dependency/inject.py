from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from ..policy import AuthIPRateLimitingPolicy, AuthMFAPolicy, AuthTokenPolicy
from ..repository import AuthDeviceRepository, AuthOneTimePinRepository, AuthTokenRepository, AuthUserRepository
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

# Inject Repositories
def get_device_repository(db: Session = Depends(get_db)) -> AuthDeviceRepository:
    return AuthDeviceRepository(db)


def get_one_time_pin_repository(db: Session = Depends(get_db)) -> AuthOneTimePinRepository:
    return AuthOneTimePinRepository(db)


def get_token_repository(db: Session = Depends(get_db)) -> AuthTokenRepository:
    return AuthTokenRepository(db)


def get_user_repository(db: Session = Depends(get_db)) -> AuthUserRepository:
    return AuthUserRepository(db)


# Inject Services
def get_auth_device_service(
    repository: AuthDeviceRepository = Depends(get_device_repository),
) -> AuthDeviceService:
    return AuthDeviceService(repository)


def get_auth_register_service(
    repository: AuthUserRepository = Depends(get_user_repository),
) -> AuthRegisterService:
    return AuthRegisterService(repository)


def get_auth_login_service(
    repository: AuthUserRepository = Depends(get_user_repository),
) -> AuthLoginService:
    return AuthLoginService(repository)


def get_auth_logout_service(
    repository: AuthUserRepository = Depends(get_user_repository),
) -> AuthLogoutService:
    return AuthLogoutService(repository)


def get_auth_one_time_pin_service(
    repository: AuthOneTimePinRepository = Depends(get_one_time_pin_repository),
) -> AuthOneTimePinService:
    return AuthOneTimePinService(repository)


def get_auth_token_service(
    repository: AuthTokenRepository = Depends(get_token_repository),
) -> AuthTokenService:
    return AuthTokenService(repository)
