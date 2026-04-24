from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.repositories.auth.user_repository import UserRepository


class FakeExecuteResult:
    def __init__(self, value) -> None:
        self.value = value

    def scalar_one_or_none(self):
        return self.value


@pytest.mark.asyncio
async def test_get_by_email_returns_scalar_result(make_user) -> None:
    user = make_user()
    db = SimpleNamespace(execute=AsyncMock(return_value=FakeExecuteResult(user)))

    result = await UserRepository(db).get_by_email("reader@example.com")

    assert result is user


@pytest.mark.asyncio
async def test_create_persists_and_refreshes_user() -> None:
    db = SimpleNamespace(add=Mock(), commit=AsyncMock(), refresh=AsyncMock())

    user = await UserRepository(db).create(
        email="reader@example.com",
        name="Reader",
        hashed_password="hashed-password",
    )

    assert user.email == "reader@example.com"
    db.add.assert_called_once_with(user)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_update_reading_goal_commits_and_refreshes_user(make_user) -> None:
    user = make_user(reading_goal=24)
    db = SimpleNamespace(commit=AsyncMock(), refresh=AsyncMock())

    result = await UserRepository(db).update_reading_goal(user, 40)

    assert result is user
    assert user.reading_goal == 40
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(user)
