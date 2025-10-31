import pytest
from fastapi.testclient import TestClient
from app.database.models.user import User
from app.core.security import verify_password

@pytest.fixture
def register_user(client: TestClient):
    payload = {
        "first_name": "Juliana",
        "last_name": "Ramírez",
        "email": "juliana@example.com",
        "password": "supersegura123"
    }
    response = client.post("/auth/register", json=payload)
    return response


def test_register_user_success(client, db_session):
    response = client.post("/auth/register", json={
        "first_name": "Juliana",
        "last_name": "Ramírez",
        "email": "juliana@example.com",
        "password": "supersegura123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "juliana@example.com"
    assert "id" in data

    user = db_session.query(User).filter(User.email == "juliana@example.com").first()
    assert user is not None
    assert verify_password("supersegura123", user.password_hash)


def test_register_user_duplicate(client):
    payload = {
        "first_name": "Diego",
        "last_name": "Acuña",
        "email": "diego@example.com",
        "password": "supersegura123"
    }
    client.post("/auth/register", json=payload)
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "El correo ya está registrado"


def test_login_success(client, register_user):
    response = client.post("/auth/login", json={
        "email": "juliana@example.com",
        "password": "supersegura123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post("/auth/login", json={
        "email": "davidfernando@example.com",
        "password": "incorrecta123"
    })
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"