from fastapi import APIRouter, Depends
from .providers import (
    get_auth_login_service,
    get_auth_logout_service,
    get_auth_one_time_pin_service,
    get_auth_register_service,
    get_auth_token_service,
)
from .schema import (
    AuthUserResponse,
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    OneTimePinRequest,
    TokenRequest,
    TokenResponse,
)
from .service import (
    AuthLoginService,
    AuthLogoutService,
    AuthOneTimePinService,
    AuthRegisterService,
    AuthTokenService,
)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=AuthUserResponse)
def register(
    data: RegisterRequest, service: AuthRegisterService = Depends(get_auth_register_service)
) -> AuthUserResponse:
    return service.register(data)


@router.post("/one-time-pin", response_model=AuthUserResponse)
def one_time_pin(
    data: OneTimePinRequest, service: AuthOneTimePinService = Depends(get_auth_one_time_pin_service)
) -> AuthUserResponse:
    return service.one_time_pin(data)


@router.post("/login", response_model=LoginResponse)
def login(
    data: LoginRequest, service: AuthLoginService = Depends(get_auth_login_service)
) -> LoginResponse:
    return service.login(data)


@router.post("/logout", response_model=LogoutResponse)
def logout(
    data: LogoutRequest, service: AuthLogoutService = Depends(get_auth_logout_service)
) -> LogoutResponse:
    return service.logout(data)


@router.patch("/refresh_token", response_model=TokenResponse)
def refresh_token(
    data: TokenRequest, service: AuthTokenService = Depends(get_auth_token_service)
) -> TokenResponse:
    return service.refresh_token(data)
