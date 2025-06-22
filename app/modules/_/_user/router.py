from typing import List
from fastapi import APIRouter, Depends
from .schema import UserCreateRequest, UserUpdateRequest, UserResponse
from .service import UserService
from .providers import get_user_service

router = APIRouter(prefix="/user", tags=["User"])


# TODO check if user is authenticated
@router.post("", response_model=UserResponse)
def create(data: UserCreateRequest, service: UserService = Depends(get_user_service)):
    pass


# TODO check if user is authenticated
@router.get("/all", response_model=List[UserResponse])
def get_all(service: UserService = Depends(get_user_service)):
    pass


# TODO check if user is authenticated
@router.get("/{id}", response_model=UserResponse)
def get_by_id(id: int, service: UserService = Depends(get_user_service)):
    pass


# TODO check if user is authenticated
@router.patch("/{id}", response_model=UserResponse)
def update(
    id: int,
    data: UserUpdateRequest,
    service: UserService = Depends(get_user_service),
):
    pass


# TODO check if user is authenticated
@router.delete("/{id}")
def delete(id: int, service: UserService = Depends(get_user_service)):
    pass
