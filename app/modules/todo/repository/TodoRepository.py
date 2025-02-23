from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from typing import List, Tuple
from app.core import BaseSortOrder
from app.database import DatabaseRepository
from ..model import Todo
from ..schema import (
    TodoCreate,
    TodoUpdate,
    TodoPaginationParams,
)


class TodoRepository:
    def __init__(self, db: Session):
        self.db = db
        self.repository = DatabaseRepository(db, Todo)

    def create(self, todo: TodoCreate) -> Todo:
        return self.repository.create(todo)

    def update(self, todo_id: int, todo_data: TodoUpdate) -> Todo | None:
        return self.repository.update(todo_id, todo_data)

    def delete(self, todo_id: int) -> bool:
        return self.repository.delete(todo_id)

    def get_by_id(self, todo_id: int) -> Todo | None:
        return self.repository.get_one(todo_id)

    def get_all(self) -> List[Todo]:
        return self.repository.query().all()

    def get_paginated(
        self, params: TodoPaginationParams
    ) -> Tuple[List[Todo], int, int, int, int]:
        query = self.repository.query()

        filters = {
            "searches": {"title": params.title, "description": params.description},
            "exact_matches": {"status": params.status, "severity": params.severity},
            "date_ranges": {
                "created_at": (params.created_at_from, params.created_at_to),
                "updated_at": (params.updated_at_from, params.updated_at_to),
            },
        }

        for field, value in filters["searches"].items():
            if value:
                query = query.filter(getattr(Todo, field).ilike(f"%{value}%"))

        for field, value in filters["exact_matches"].items():
            if value:
                query = query.filter(getattr(Todo, field) == value)

        for field, (date_from, date_to) in filters["date_ranges"].items():
            if date_from:
                query = query.filter(getattr(Todo, field) >= date_from)
            if date_to:
                query = query.filter(getattr(Todo, field) <= date_to)

        # Sorting
        sort_column = getattr(Todo, params.sort_by)
        query = query.order_by(
            desc(sort_column)
            if params.sort_order == BaseSortOrder.DESC
            else asc(sort_column)
        )

        # Paginate
        total = query.count()
        items = (
            query.offset((params.page - 1) * params.page_size)
            .limit(params.page_size)
            .all()
        )

        return (
            items,  # List of items
            total,  # Total items
            params.page,  # Current page
            params.page_size,  # Items per page
            (total + params.page_size - 1) // params.page_size,  # Total pages
        )
