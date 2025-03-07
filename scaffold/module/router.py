from typing import List
from fastapi import APIRouter, Depends
from .schema import {Module}Create, {Module}Update, {Module}Response
from .service import {Module}Service
from .providers import get_{module}_service

router = APIRouter(prefix="/{module}", tags=["{Module}"])


@router.post("", response_model={Module}Response)
def create(
    data: {Module}Create, service: {Module}Service = Depends(get_{module}_service)
):
    pass


@router.get("/all", response_model=List[{Module}Response])
def get_all(service: {Module}Service = Depends(get_{module}_service)):
    pass


@router.get("/{id}", response_model={Module}Response)
def get_by_id(id: int, service: {Module}Service = Depends(get_{module}_service)):
    pass


@router.patch("/{id}", response_model={Module}Response)
def update(
    id: int,
    data: {Module}Update,
    service: {Module}Service = Depends(get_{module}_service),
):
    pass


@router.delete("/{id}")
def delete(id: int, service: {Module}Service = Depends(get_{module}_service)):
    pass
