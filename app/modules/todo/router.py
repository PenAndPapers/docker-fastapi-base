from typing import List
from fastapi import APIRouter, Depends, Request
from app.core import BasePaginatedResponse, cache_response
from .constants import (
    CREATE_TODO_DOC,
    GET_PAGINATED_TODOS_DOC,
    GET_TODO_DOC,
    GET_ALL_TODOS_DOC,
    UPDATE_TODO_DOC,
    DELETE_TODO_DOC,
)
from .providers import get_todo_service
from .service import TodoService
from .schema import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoPaginationParams,
)


router = APIRouter(prefix="/todos", tags=["Todos"])


@router.post("", response_model=TodoResponse, description=CREATE_TODO_DOC)
def create_todo(
    todo: TodoCreate, todo_service: TodoService = Depends(get_todo_service)
) -> TodoResponse:
    return todo_service.create(todo)


@router.get("/all", response_model=List[TodoResponse], description=GET_ALL_TODOS_DOC)
@cache_response(expiry=10)
def get_all_todos(
    request: Request, todo_service: TodoService = Depends(get_todo_service)
) -> List[TodoResponse]:
    return todo_service.get_all()


@router.get(
    "/paginated",
    response_model=BasePaginatedResponse,
    description=GET_PAGINATED_TODOS_DOC,
)
@cache_response(expiry=10)
async def get_paginated_todos(
    request: Request,
    params: TodoPaginationParams = Depends(),
    todo_service: TodoService = Depends(get_todo_service),
) -> BasePaginatedResponse:
    response = todo_service.get_paginated(params)
    # Convert SQLAlchemy models to dicts before returning
    response.items = [
        TodoResponse.model_validate(item).model_dump() for item in response.items
    ]
    return response


@router.get("/{id}", response_model=TodoResponse, description=GET_TODO_DOC)
@cache_response(expiry=10)
def get_todo(
    request: Request,
    id: int,
    todo_service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    return todo_service.get_by_id(id)


@router.patch("/{id}", response_model=TodoResponse, description=UPDATE_TODO_DOC)
def update_todo(
    id: int,
    todo: TodoUpdate,
    todo_service: TodoService = Depends(get_todo_service),
) -> TodoResponse:
    return todo_service.update(id, todo)


@router.delete("/{id}", status_code=204, description=DELETE_TODO_DOC)
def delete_todo(id: int, todo_service: TodoService = Depends(get_todo_service)) -> None:
    todo_service.delete(id)
