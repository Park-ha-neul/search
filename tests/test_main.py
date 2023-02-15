from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_read_main():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "Hello": "T3Q.search API Application!",
        "Swagger UI": "/docs",
        "ReDoc": "/redoc",
    }
