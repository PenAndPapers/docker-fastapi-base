from typing import List
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/user", tags=["User"])

# TODO: IMPLEMENT THIS ENDPOINT

@router.get("/all", response_model=None)
def get_users() -> None:
    """
    Get all users
    """
    pass

@router.post("/", response_model=None)
def create_user() -> None:
    """
    Create user
    """
    pass

@router.get("/", response_model=None)
def get_user() -> None:
    """
    Get user
    """
    pass

@router.patch("/", response_model=None)
def update_user() -> None:
    """
    Update user
    """
    pass

@router.delete("/", response_model=None)
def delete_user() -> None:
    """
    Delete user
    """
    pass