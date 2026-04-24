from unittest.mock import AsyncMock, Mock

import pytest

from app.core.security import get_password_hash, verify_password
from app.schemas.users import UserCreate
from app.services.auth.auth_service import AuthService


@pytest.mark.asyncio
async def test_register_user_creates_hashed_password(make_user) -> None:
    repository = Mock()
    repository.get_by_email = AsyncMock(return_value=None)
    repository.create = AsyncMock(return_value=make_user())
    service = AuthService(repository)
    payload = UserCreate(email="reader@example.com", name="Reader", password="password123")

    user = await service.register_user(payload)

    assert user.email == "reader@example.com"
    repository.create.assert_awaited_once()
    hashed_password = repository.create.await_args.kwargs["hashed_password"]
    assert hashed_password != payload.password
    assert verify_password(payload.password, hashed_password) is True


@pytest.mark.asyncio
async def test_register_user_returns_none_when_email_already_exists(make_user) -> None:
    repository = Mock()
    repository.get_by_email = AsyncMock(return_value=make_user())
    repository.create = AsyncMock()
    service = AuthService(repository)

    result = await service.register_user(
        UserCreate(email="reader@example.com", name="Reader", password="password123")
    )

    assert result is None
    repository.create.assert_not_called()


@pytest.mark.asyncio
async def test_authenticate_user_returns_user_when_password_matches(make_user) -> None:
    repository = Mock()
    password = "password123"
    user = make_user(hashed_password=get_password_hash(password))
    repository.get_by_email = AsyncMock(return_value=user)
    service = AuthService(repository)

    result = await service.authenticate_user("reader@example.com", password)

    assert result is user


@pytest.mark.asyncio
async def test_authenticate_user_returns_none_for_unknown_email() -> None:
    repository = Mock()
    repository.get_by_email = AsyncMock(return_value=None)
    service = AuthService(repository)

    result = await service.authenticate_user("reader@example.com", "password123")

    assert result is None


@pytest.mark.asyncio
async def test_authenticate_user_returns_none_for_wrong_password(make_user) -> None:
    repository = Mock()
    user = make_user(hashed_password=get_password_hash("good-password"))
    repository.get_by_email = AsyncMock(return_value=user)
    service = AuthService(repository)

    result = await service.authenticate_user("reader@example.com", "bad-password")

    assert result is None
