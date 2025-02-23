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
from .controller import TodoController
from .providers import get_todo_controller
from .schema import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoPaginationParams,
)


router = APIRouter(prefix="/todos", tags=["todos"])


@router.post("", response_model=TodoResponse, description=CREATE_TODO_DOC)
def create_todo(
    todo: TodoCreate, todo_controller: TodoController = Depends(get_todo_controller)
) -> TodoResponse:
    return todo_controller.create_todo(todo)


@router.get("/all", response_model=List[TodoResponse], description=GET_ALL_TODOS_DOC)
@cache_response(expiry=10)
def get_all_todos(
    request: Request, todo_controller: TodoController = Depends(get_todo_controller)
) -> List[TodoResponse]:
    return todo_controller.get_all_todos()


@router.get(
    "/paginated",
    response_model=BasePaginatedResponse,
    description=GET_PAGINATED_TODOS_DOC,
)
@cache_response(expiry=10)
async def get_paginated_todos(
    request: Request,
    params: TodoPaginationParams = Depends(),
    todo_controller: TodoController = Depends(get_todo_controller),
) -> BasePaginatedResponse:
    response = todo_controller.get_paginated_todos(params)
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
    todo_controller: TodoController = Depends(get_todo_controller),
) -> TodoResponse:
    return todo_controller.get_todo(id)


@router.patch("/{id}", response_model=TodoResponse, description=UPDATE_TODO_DOC)
def update_todo(
    id: int,
    todo: TodoUpdate,
    todo_controller: TodoController = Depends(get_todo_controller),
) -> TodoResponse:
    return todo_controller.update_todo(id, todo)


@router.delete("/{id}", status_code=204, description=DELETE_TODO_DOC)
def delete_todo(
    id: int, todo_controller: TodoController = Depends(get_todo_controller)
) -> None:
    todo_controller.delete_todo(id)
