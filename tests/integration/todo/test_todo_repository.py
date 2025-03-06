import json
import pytest
from pydantic.json import pydantic_encoder
from sqlalchemy.orm import Session
from app.modules.todo.repository import TodoRepository
from app.modules.todo.constants import TodoSeverityEnum, TodoStatusEnum
from app.modules.todo.schema import TodoCreate


@pytest.fixture
def repository(db_session: Session):
    return TodoRepository(db_session)


@pytest.fixture
def todo_details():
    return {
        "title": "This is a test Todo",
        "description": "This is a test Description",
        "severity": TodoSeverityEnum.LOW,
        "status": TodoStatusEnum.TODO,
    }


def extract_todo_dict(todo):
    return {
        "title": todo.title,
        "description": todo.description,
        "severity": todo.severity,
        "status": todo.status,
    }


def dump_data(data):
    return json.dumps(data, sort_keys=True, default=pydantic_encoder)


def test_create(db_session: Session, repository: TodoRepository, todo_details: dict):
    # Create test data
    todo_data = TodoCreate(**todo_details)

    # Test create operation
    response = repository.create(todo_data)
    db_session.commit()

    # Assertions
    assert response.id is not None
    assert extract_todo_dict(response) == extract_todo_dict(todo_data)


def test_get_by_id(db_session: Session, repository: TodoRepository, todo_details: dict):
    # Create test data
    todo_data = TodoCreate(**todo_details)
    created_todo = repository.create(todo_data)
    db_session.commit()

    # Test retrieve operation
    response = repository.get_by_id(created_todo.id)

    # Assertions
    assert response is not None
    assert response.id == created_todo.id
    assert extract_todo_dict(response) == extract_todo_dict(todo_data)


def test_get_all(db_session: Session, repository: TodoRepository, todo_details: dict):
    # Create test data
    todo_data = TodoCreate(**todo_details)
    repository.create(todo_data)
    db_session.commit()

    # Test retrieve all operation
    response = repository.get_all()

    # Assertions
    assert response is not None
    assert len(response) >= 1


def test_update(db_session: Session, repository: TodoRepository, todo_details: dict):
    # Create test data
    todo_data = TodoCreate(**todo_details)
    created_todo = repository.create(todo_data)
    db_session.commit()

    # Test update operation
    updated_data = TodoCreate(
        title="Updated Title",
        description="Updated Description",
        severity=TodoSeverityEnum.MEDIUM,
        status=TodoStatusEnum.IN_PROGRESS,
    )
    response = repository.update(created_todo.id, updated_data)

    # Assertions
    assert response is not None
    assert response.id == created_todo.id
    assert extract_todo_dict(response) == extract_todo_dict(updated_data)


def test_delete(db_session: Session, repository: TodoRepository, todo_details: dict):
    # Create test data
    todo_data = TodoCreate(**todo_details)
    created_todo = repository.create(todo_data)
    db_session.commit()

    # Test delete operation
    response = repository.delete(created_todo.id)

    # Assertions
    assert response is True
