import json
import pytest
from unittest.mock import Mock
from pydantic.json import pydantic_encoder
from app.modules.todo.service import TodoService
from app.modules.todo.schema import TodoCreate, TodoPaginationParams
from app.modules.todo.constants import (
    TodoSeverityEnum,
    TodoStatusEnum,
    TodoSortFieldsEnum,
)
from app.modules.todo.model import Todo


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def mock_policy():
    return Mock()


@pytest.fixture
def todo_service(mock_repository, mock_policy):
    return TodoService(repository=mock_repository, policy=mock_policy)


@pytest.fixture
def todo_details():
    return {
        "title": "This is a test Todo",
        "description": "This is a test Description",
        "severity": TodoSeverityEnum.LOW,
        "status": TodoStatusEnum.TODO,
    }


@pytest.fixture
def todo_response_data(todo_details):
    return Todo(id=1, **todo_details)


@pytest.fixture
def create_request_data(todo_details):
    return TodoCreate(**todo_details)


def dump_data(data):
    return json.dumps(data, sort_keys=True, default=pydantic_encoder)


def extract_todo_dict(todo: Todo):
    return {
        "title": todo.title,
        "description": todo.description,
        "severity": todo.severity,
        "status": todo.status,
    }


def test_create(todo_service, mock_repository, todo_response_data, create_request_data):
    # mock repository return value
    mock_repository.create.return_value = todo_response_data

    # call the service method
    result = todo_service.create(create_request_data)

    # assertions
    mock_repository.create.assert_called_once()

    # check id
    assert result.id == 1

    # compare relevant attributes
    result_dict = {
        "title": result.title,
        "description": result.description,
        "severity": result.severity,
        "status": result.status,
    }
    create_data_dict = create_request_data.model_dump(exclude={"id"})

    # compare dictionaries
    assert dump_data(result_dict) == dump_data(create_data_dict)


def test_get_paginated(todo_service, mock_repository, todo_details):
    # create test data
    todos = [Todo(id=i, **todo_details) for i in range(1, 22)]

    # mock repository return value
    mock_repository.get_paginated.return_value = (
        todos[:10],  # First 10 items for current page
        11,  # Total items
        1,  # Current page
        10,  # Items per page
        3,  # Total pages
    )

    # create pagination params
    params = TodoPaginationParams(
        title="This is a test Todo",
        description="",
        status=TodoStatusEnum.TODO,
        severity=TodoSeverityEnum.LOW,
        sort_by=TodoSortFieldsEnum.CREATED_AT,
    )

    # call the service method
    result = todo_service.get_paginated(params)

    # assertions
    mock_repository.get_paginated.assert_called_once_with(params)
    assert len(result.items) == 10
    assert result.items[0].id == 1
    assert result.total == 11
    assert result.current_page == 1
    assert result.per_page == 10
    assert result.pages == 3
    assert result.has_next is True
    assert result.has_prev is False


def test_get_by_id(todo_service, mock_repository, todo_response_data):
    # mock repository return value
    mock_repository.get_by_id.return_value = todo_response_data
    # call the service method
    result = todo_service.get_by_id(1)
    # assertions
    mock_repository.get_by_id.assert_called_once()
    # check id
    assert result.id == 1
    # compare dictionaries
    assert dump_data(extract_todo_dict(result)) == dump_data(
        extract_todo_dict(todo_response_data)
    )


def test_get_all(todo_service, mock_repository, todo_details):
    # create test data
    first_todo = Todo(id=1, **todo_details)
    second_todo = Todo(id=2, **todo_details)
    third_todo = Todo(id=3, **todo_details)

    # mock repository return value
    mock_repository.get_all.return_value = [first_todo, second_todo, third_todo]
    # call the service method
    result = todo_service.get_all()
    # assertions
    mock_repository.get_all.assert_called_once()
    # check length
    assert len(result) == 3
    # check ids
    assert result[0].id == 1
    assert result[1].id == 2
    assert result[2].id == 3


def test_update(todo_service, mock_repository, todo_response_data):
    updated_details = todo_response_data
    updated_details.severity = TodoSeverityEnum.MEDIUM
    updated_details.status = TodoStatusEnum.IN_PROGRESS

    # mock repository return value
    mock_repository.update.return_value = updated_details

    # call the service method
    result = todo_service.update(1, updated_details)
    # assertions
    mock_repository.update.assert_called_once()
    # check id
    assert result.id == 1
    # compare dictionaries
    assert dump_data(extract_todo_dict(result)) == dump_data(
        extract_todo_dict(todo_response_data)
    )


def test_delete(todo_service, mock_repository):
    # mock repository return value
    mock_repository.delete.return_value = None
    # call the service method
    result = todo_service.delete(1)
    # assertions
    mock_repository.delete.assert_called_once()
    assert result is None
