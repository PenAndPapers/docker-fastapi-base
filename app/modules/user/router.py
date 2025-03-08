from typing import List
from fastapi import APIRouter, Depends
from .schema import UserCreate, UserUpdate, UserResponse
from .service import UserService
from .providers import get_user_service

router = APIRouter(prefix="/user", tags=["User"])


@router.post("", response_model=UserResponse)
def create(data: UserCreate, service: UserService = Depends(get_user_service)):
    pass


@router.get("/all", response_model=List[UserResponse])
def get_all(service: UserService = Depends(get_user_service)):
    pass


@router.get("/{id}", response_model=UserResponse)
def get_by_id(id: int, service: UserService = Depends(get_user_service)):
    pass


@router.patch("/{id}", response_model=UserResponse)
def update(
    id: int,
    data: UserUpdate,
    service: UserService = Depends(get_user_service),
):
    pass


@router.delete("/{id}")
def delete(id: int, service: UserService = Depends(get_user_service)):
    pass
