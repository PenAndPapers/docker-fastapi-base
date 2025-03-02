import json
import pytest
from unittest.mock import Mock
from pydantic.json import pydantic_encoder
from app.modules.todo.service import TodoService
from app.modules.todo.schema import TodoCreate
from app.modules.todo.constants import TodoSeverityEnum, TodoStatusEnum
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
