import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.modules.todo.constants import TodoSeverityEnum, TodoStatusEnum
from app.database.session import get_db


@pytest.fixture
def client(db_session, mock_redis):
    app.state.redis = mock_redis
    app.dependency_overrides[get_db] = lambda: db_session
    yield TestClient(app)
    app.dependency_overrides.clear()
    delattr(app.state, "redis")


@pytest.fixture
def todo_data():
    return {
        "title": "This is a test Todo",
        "description": "This is a test Description",
        "severity": TodoSeverityEnum.LOW.value,
        "status": TodoStatusEnum.TODO.value,
    }


@pytest.fixture
def todo_update_data():
    return {
        "title": "This is a test Todo Updated",
        "description": "This is a test Description Updated",
        "severity": TodoSeverityEnum.MEDIUM.value,
        "status": TodoStatusEnum.IN_PROGRESS.value,
    }


def get_json_format(response):
    return response.json()


def test_create(client: TestClient, todo_data):
    response = client.post("/todos", json=todo_data)
    assert response.status_code == 200
    assert response is not None

    res = get_json_format(response)

    assert res["id"] is not None
    assert res["title"] == todo_data["title"]
    assert res["created_at"] is not None
    assert res["updated_at"] is not None


def test_get_by_id(client: TestClient, todo_data):
    create_response = client.post("/todos", json=todo_data)
    assert create_response.status_code == 200
    assert create_response is not None

    res = get_json_format(create_response)
    id = res["id"]

    get_response = client.get(f"/todos/{id}")
    assert get_response.status_code == 200

    todo = get_json_format(get_response)
    assert todo["id"] is not None
    assert todo["title"] == todo_data["title"]


def test_get_all(client: TestClient, todo_data):
    create_response = client.post("/todos", json=todo_data)
    assert create_response.status_code == 200
    assert create_response is not None

    get_response = client.get("/todos/all")
    assert get_response.status_code == 200

    res = get_json_format(get_response)

    assert res is not None
    assert isinstance(res, list)
    assert len(res) > 0


def test_update(client: TestClient, todo_data, todo_update_data):
    create_response = client.post("/todos", json=todo_data)
    assert create_response.status_code == 200
    assert create_response is not None

    res = get_json_format(create_response)
    id = res["id"]

    update_response = client.patch(f"/todos/{id}", json=todo_update_data)

    assert update_response.status_code == 200
    assert update_response is not None

    update_res = get_json_format(update_response)

    # Assertions
    assert update_res["id"] == res["id"]
    assert update_res["title"] == todo_update_data["title"]
    assert update_res["updated_at"] != res["updated_at"]


def test_delete(client: TestClient, todo_data):
    create_response = client.post("/todos", json=todo_data)
    assert create_response.status_code == 200
    assert create_response is not None

    res = get_json_format(create_response)
    id = res["id"]

    delete_response = client.delete(f"/todos/{id}")
    assert delete_response.status_code == 204
