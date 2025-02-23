from typing import List
from app.core import BasePaginatedResponse
from .TodoPolicy import TodoPolicy
from ..model import Todo
from ..repository import TodoRepository
from ..schema import (
    TodoCreate,
    TodoUpdate,
    TodoResponse,
    TodoPaginationParams,
)


class TodoService:
    def __init__(
        self,
        repository: TodoRepository,
        policy: TodoPolicy,
    ):
        self.repository = repository
        self.policy = policy

    def create(self, todo_data: TodoCreate) -> Todo:
        """
        Create a new todo.
        """
        return self.repository.create(todo_data)

    def get_paginated(
        self, params: TodoPaginationParams
    ) -> BasePaginatedResponse[TodoResponse]:
        """
        Get paginated todos.
        """
        items, total, current_page, per_page, pages = self.repository.get_paginated(
            params
        )

        return BasePaginatedResponse(
            items=items,
            total=total,
            current_page=current_page,
            per_page=per_page,
            pages=pages,
            has_next=current_page < pages,
            has_prev=current_page > 1,
        )

    def get_by_id(self, todo_id: int) -> Todo:
        """
        Get a todo by its ID.
        """
        return self.repository.get_by_id(todo_id)

    def get_all(self) -> List[Todo]:
        """
        Get all todos.
        """
        return self.repository.get_all()

    def update(self, todo_id: int, todo_data: TodoUpdate) -> Todo:
        """
        Update a todo by its ID.
        If the status is being updated, validate the status and severity transition.
        """
        current_todo = self.get_by_id(todo_id)
        if todo_data.status is not None:
            self.policy.validate_status_transition(
                current_todo.status, todo_data.status
            )
        if todo_data.severity is not None:
            self.policy.validate_severity_transition(
                current_todo.severity, todo_data.severity
            )
        return self.repository.update(todo_id, todo_data)

    def delete(self, todo_id: int) -> None:
        """
        Delete a todo by its ID
        """
        self.get_by_id(todo_id)
        self.repository.delete(todo_id)
