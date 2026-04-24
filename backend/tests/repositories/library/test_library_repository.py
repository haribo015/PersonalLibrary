from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.repositories.library.library_repository import LibraryRepository


class FakeScalars:
    def __init__(self, values) -> None:
        self.values = values

    def unique(self):
        return self

    def all(self):
        return self.values


class FakeExecuteResult:
    def __init__(self, *, scalar=None, values=None) -> None:
        self.scalar = scalar
        self.values = values or []

    def scalar_one_or_none(self):
        return self.scalar

    def scalars(self):
        return FakeScalars(self.values)


@pytest.mark.asyncio
async def test_list_for_user_returns_unique_items(make_library_item) -> None:
    items = [make_library_item(id=1), make_library_item(id=2, book_id=2)]
    db = SimpleNamespace(execute=AsyncMock(return_value=FakeExecuteResult(values=items)))

    result = await LibraryRepository(db).list_for_user(1)

    assert result == items


@pytest.mark.asyncio
async def test_get_for_user_and_book_returns_scalar_result(make_library_item) -> None:
    item = make_library_item()
    db = SimpleNamespace(execute=AsyncMock(return_value=FakeExecuteResult(scalar=item)))

    result = await LibraryRepository(db).get_for_user_and_book(1, 1)

    assert result is item


@pytest.mark.asyncio
async def test_create_builds_default_item_and_reloads_book(make_book, make_library_item) -> None:
    book = make_book(id=9)
    item = make_library_item(book=book, book_id=book.id)
    db = SimpleNamespace(add=Mock(), commit=AsyncMock())
    repository = LibraryRepository(db)
    repository.get_for_user_and_book = AsyncMock(return_value=item)

    result = await repository.create(user_id=3, book=book)

    assert result is item
    created_item = db.add.call_args.args[0]
    assert created_item.user_id == 3
    assert created_item.book_id == 9
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_with_metadata_builds_item_with_payload(make_book, make_library_item) -> None:
    book = make_book(id=11)
    item = make_library_item(book=book, book_id=book.id, category="Fantasy")
    db = SimpleNamespace(add=Mock(), commit=AsyncMock())
    repository = LibraryRepository(db)
    repository.get_for_user_and_book = AsyncMock(return_value=item)

    result = await repository.create_with_metadata(
        user_id=4,
        book=book,
        metadata={"category": "Fantasy", "favorite": True},
    )

    assert result is item
    created_item = db.add.call_args.args[0]
    assert created_item.category == "Fantasy"
    assert created_item.favorite is True
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_sets_attributes_and_refreshes(make_library_item) -> None:
    item = make_library_item(priority="low")
    db = SimpleNamespace(commit=AsyncMock(), refresh=AsyncMock())

    result = await LibraryRepository(db).update(item, {"priority": "high", "favorite": True})

    assert result is item
    assert item.priority == "high"
    assert item.favorite is True
    db.commit.assert_awaited_once()
    db.refresh.assert_awaited_once_with(item)


@pytest.mark.asyncio
async def test_delete_for_user_and_book_deletes_library_item_and_review() -> None:
    db = SimpleNamespace(execute=AsyncMock(), commit=AsyncMock())

    await LibraryRepository(db).delete_for_user_and_book(7, 12)

    assert db.execute.await_count == 2
    db.commit.assert_awaited_once()
