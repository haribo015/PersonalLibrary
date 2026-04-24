from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.routes.api_v1 import dependencies as dependencies_module


@pytest.mark.asyncio
async def test_get_current_user_rejects_invalid_token(monkeypatch) -> None:
    monkeypatch.setattr(dependencies_module, "decode_access_token", lambda token: None)

    with pytest.raises(HTTPException) as exc:
        await dependencies_module.get_current_user(token="bad-token", db=object())

    assert exc.value.status_code == 401
    assert exc.value.headers == {"WWW-Authenticate": "Bearer"}


@pytest.mark.asyncio
async def test_get_current_user_rejects_missing_user(monkeypatch) -> None:
    monkeypatch.setattr(dependencies_module, "decode_access_token", lambda token: {"sub": "reader@example.com"})
    monkeypatch.setattr(
        dependencies_module,
        "UserRepository",
        lambda db: SimpleNamespace(get_by_email=AsyncMock(return_value=None)),
    )

    with pytest.raises(HTTPException) as exc:
        await dependencies_module.get_current_user(token="good-token", db=object())

    assert exc.value.status_code == 401
    assert exc.value.detail == "Utilisateur introuvable"


@pytest.mark.asyncio
async def test_get_current_user_returns_loaded_user(monkeypatch, make_user) -> None:
    user = make_user()
    monkeypatch.setattr(dependencies_module, "decode_access_token", lambda token: {"sub": user.email})
    monkeypatch.setattr(
        dependencies_module,
        "UserRepository",
        lambda db: SimpleNamespace(get_by_email=AsyncMock(return_value=user)),
    )

    result = await dependencies_module.get_current_user(token="good-token", db=object())

    assert result is user


def test_get_current_active_user_rejects_inactive_user(make_user) -> None:
    with pytest.raises(HTTPException) as exc:
        dependencies_module.get_current_active_user(make_user(is_active=False))

    assert exc.value.status_code == 400


def test_get_current_active_user_returns_active_user(make_user) -> None:
    user = make_user(is_active=True)

    assert dependencies_module.get_current_active_user(user) is user


@pytest.mark.asyncio
async def test_get_optional_current_user_returns_none_without_token() -> None:
    assert await dependencies_module.get_optional_current_user(token=None, db=object()) is None


@pytest.mark.asyncio
async def test_get_optional_current_user_returns_none_for_invalid_payload(monkeypatch) -> None:
    monkeypatch.setattr(dependencies_module, "decode_access_token", lambda token: {"foo": "bar"})

    assert await dependencies_module.get_optional_current_user(token="bad-token", db=object()) is None


@pytest.mark.asyncio
async def test_get_optional_current_user_returns_user_when_token_is_valid(monkeypatch, make_user) -> None:
    user = make_user()
    monkeypatch.setattr(dependencies_module, "decode_access_token", lambda token: {"sub": user.email})
    monkeypatch.setattr(
        dependencies_module,
        "UserRepository",
        lambda db: SimpleNamespace(get_by_email=AsyncMock(return_value=user)),
    )

    result = await dependencies_module.get_optional_current_user(token="good-token", db=object())

    assert result is user
