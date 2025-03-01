from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_create_todo_api():
    response = client.post(
        "/todos/", json={"title": "Test todo", "description": "Test description"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Test todo"
