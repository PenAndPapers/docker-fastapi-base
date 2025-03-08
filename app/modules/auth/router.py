from fastapi import APIRouter, Depends
from .schema import (
    AuthRegister,
    AuthRegisterResponse,
    AuthLogin,
    AuthLoginResponse,
    AuthLogout,
    AuthLogoutResponse,
    AuthToken,
    AuthTokenResponse,
)
from .service import AuthService
from .providers import get_auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthRegisterResponse)
def register(
    data: AuthRegister, service: AuthService = Depends(get_auth_service)
) -> AuthRegisterResponse:
    return service.register(data)


@router.post("/login", response_model=AuthLoginResponse)
def login(
    data: AuthLogin, service: AuthService = Depends(get_auth_service)
) -> AuthLoginResponse:
    return service.login(data)


@router.post("/logout", response_model=AuthLogoutResponse)
def logout(
    data: AuthLogout, service: AuthService = Depends(get_auth_service)
) -> AuthLogoutResponse:
    return service.logout(data)


@router.patch("/refresh_token", response_model=AuthTokenResponse)
def refresh_token(
    data: AuthToken, service: AuthService = Depends(get_auth_service)
) -> AuthTokenResponse:
    return service.refresh_token(data)
