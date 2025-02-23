from typing import List
from app.core import BasePaginatedResponse
from ..service import TodoService
from ..schema import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoPaginationParams,
)


class TodoController:
    def __init__(self, service: TodoService):  # Takes service as dependency
        self.service = service

    def create_todo(self, todo: TodoCreate) -> TodoResponse:
        return self.service.create(todo)

    def get_paginated_todos(
        self, params: TodoPaginationParams
    ) -> BasePaginatedResponse[TodoResponse]:
        return self.service.get_paginated(params)

    def get_todo(self, todo_id: int) -> TodoResponse:
        return self.service.get_by_id(todo_id)

    def get_all_todos(self) -> List[TodoResponse]:
        return self.service.get_all()

    def update_todo(self, todo_id: int, todo: TodoUpdate) -> TodoResponse:
        return self.service.update(todo_id, todo)

    def delete_todo(self, todo_id: int) -> None:
        self.service.delete(todo_id)
