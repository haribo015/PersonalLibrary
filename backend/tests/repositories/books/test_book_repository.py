from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.repositories.books.book_repository import BookRepository


class FakeExecuteResult:
    def __init__(self, value) -> None:
        self.value = value

    def scalar_one_or_none(self):
        return self.value


@pytest.mark.asyncio
async def test_getters_return_scalar_result(make_book) -> None:
    book = make_book()
    db = SimpleNamespace(execute=AsyncMock(side_effect=[FakeExecuteResult(book), FakeExecuteResult(book)]))
    repository = BookRepository(db)

    assert await repository.get_by_id(1) is book
    assert await repository.get_by_google_book_id("google-1") is book


@pytest.mark.asyncio
async def test_upsert_updates_existing_book(make_book) -> None:
    book = make_book(title="Old title")
    db = SimpleNamespace(commit=AsyncMock(), refresh=AsyncMock(), add=Mock())
    repository = BookRepository(db)
    repository.get_by_google_book_id = AsyncMock(return_value=book)

    result = await repository.upsert_from_google_payload(
        google_book_id="google-1",
        title="New title",
        authors="Alice, Bob",
        description="Updated",
        cover_image="https://example.com/cover.jpg",
        published_date="2025-01-01",
    )

    assert result is book
    assert book.title == "New title"
    db.add.assert_not_called()
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(book)


@pytest.mark.asyncio
async def test_upsert_creates_new_book() -> None:
    db = SimpleNamespace(commit=AsyncMock(), refresh=AsyncMock(), add=Mock())
    repository = BookRepository(db)
    repository.get_by_google_book_id = AsyncMock(return_value=None)

    book = await repository.upsert_from_google_payload(
        google_book_id="google-1",
        title="Testing Handbook",
        authors="Alice",
        description="Guide",
        cover_image="https://example.com/cover.jpg",
        published_date="2025",
    )

    assert book.google_book_id == "google-1"
    db.add.assert_called_once_with(book)
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(book)
