from fastapi import APIRouter, Depends
from .schema import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    OneTimePinRequest,
    OneTimePinResponse,
    TokenRequest,
    TokenResponse,
)
from .service import AuthService
from .providers import get_auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=RegisterResponse)
def register(
    data: RegisterRequest, service: AuthService = Depends(get_auth_service)
) -> RegisterResponse:
    return service.register(data)


@router.post("/login", response_model=LoginResponse)
def login(
    data: LoginRequest, service: AuthService = Depends(get_auth_service)
) -> LoginResponse:
    return service.login(data)


@router.post("/one-time-pin", response_model=OneTimePinResponse)
def one_time_pin(
    data: OneTimePinRequest, service: AuthService = Depends(get_auth_service)
) -> OneTimePinResponse:
    return service.one_time_pin(data)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    data: LogoutRequest, service: AuthService = Depends(get_auth_service)
) -> LogoutResponse:
    return service.logout(data)


@router.patch("/refresh_token", response_model=TokenResponse)
def refresh_token(
    data: TokenRequest, service: AuthService = Depends(get_auth_service)
) -> TokenResponse:
    return service.refresh_token(data)
