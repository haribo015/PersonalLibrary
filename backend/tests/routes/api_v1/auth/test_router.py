from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.routes.api_v1.auth import router as auth_router_module


def test_register_user_returns_created_user(build_client, monkeypatch) -> None:
    service = SimpleNamespace(
        register_user=AsyncMock(
            return_value={
                "id": 1,
                "email": "reader@example.com",
                "name": "Reader",
                "is_active": True,
                "reading_goal": 24,
            }
        )
    )
    monkeypatch.setattr(auth_router_module, "AuthService", lambda repository: service)
    client = build_client(auth_router_module.router, prefix="/api/v1/auth")

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "reader@example.com", "name": "Reader", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == "reader@example.com"


def test_register_user_returns_400_when_email_is_taken(build_client, monkeypatch) -> None:
    service = SimpleNamespace(register_user=AsyncMock(return_value=None))
    monkeypatch.setattr(auth_router_module, "AuthService", lambda repository: service)
    client = build_client(auth_router_module.router, prefix="/api/v1/auth")

    response = client.post(
        "/api/v1/auth/register",
        json={"email": "reader@example.com", "name": "Reader", "password": "password123"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email deja utilise"


def test_login_for_access_token_returns_bearer_token(build_client, monkeypatch, make_user) -> None:
    service = SimpleNamespace(authenticate_user=AsyncMock(return_value=make_user()))
    monkeypatch.setattr(auth_router_module, "AuthService", lambda repository: service)
    monkeypatch.setattr(auth_router_module, "create_access_token", lambda data, expires_delta: "token-123")
    client = build_client(auth_router_module.router, prefix="/api/v1/auth")

    response = client.post(
        "/api/v1/auth/token",
        data={"username": "reader@example.com", "password": "password123"},
    )

    assert response.status_code == 200
    assert response.json() == {"access_token": "token-123", "token_type": "bearer"}


def test_login_for_access_token_returns_401_for_invalid_credentials(build_client, monkeypatch) -> None:
    service = SimpleNamespace(authenticate_user=AsyncMock(return_value=None))
    monkeypatch.setattr(auth_router_module, "AuthService", lambda repository: service)
    client = build_client(auth_router_module.router, prefix="/api/v1/auth")

    response = client.post(
        "/api/v1/auth/token",
        data={"username": "reader@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401
