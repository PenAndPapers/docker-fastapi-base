from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db
from ..repository import TodoRepository
from ..service import TodoService, TodoPolicy

"""
This method is used to get the todo repository
depends on the database session
"""


def get_todo_repository(db: Session = Depends(get_db)) -> TodoRepository:
    return TodoRepository(db)


"""
This method is used to get the todo service
depends on the todo repository and policy
"""


def get_todo_service(
    repository: TodoRepository = Depends(get_todo_repository),
    policy: TodoPolicy = Depends(),
) -> TodoService:
    return TodoService(repository, policy)
