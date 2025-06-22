from fastapi import APIRouter, Depends

router = APIRouter(prefix="/auth", tags=["Auth"])

# TODO: IMPLEMENT THIS ENDPOINT

@router.post("/register", response_model=None)
def register() -> None:
    """
    Register a new user
    """
    pass

@router.post("/verify", response_model=None)
def verify() -> None:
    """
    Verify a user
    """
    pass

@router.post("/login", response_model=None)
def login() -> None:
    """
    Login a user
    """
    pass

@router.post("/logout", response_model=None)
def logout() -> None:
    """
    Logout a user
    """
    pass


@router.post("/refresh", response_model=None)
def refresh() -> None:
    """
    Refresh a user's token
    """
    pass


@router.post("/forgot-password", response_model=None)
def forgot_password() -> None:
    """
    Send's a forgot password email
    """
    pass