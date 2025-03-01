from fastapi.testclient import TestClient
from app.main import app  # Changed to absolute import

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "This is a web application"}


def test_redis_test():
    response = client.get("/redis-test")
    assert response.status_code == 200
    assert "hits" in response.json()
