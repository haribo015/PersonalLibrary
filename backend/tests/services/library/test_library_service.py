from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.schemas.library import LibraryItemCreate, LibraryItemUpdate
from app.services.library.library_service import LibraryService


@pytest.mark.asyncio
async def test_list_library_delegates_to_repository() -> None:
    expected_items = [SimpleNamespace(id=1)]
    library_repository = SimpleNamespace(list_for_user=AsyncMock(return_value=expected_items))
    service = LibraryService(library_repository, SimpleNamespace())

    result = await service.list_library(7)

    assert result == expected_items
    library_repository.list_for_user.assert_awaited_once_with(7)


@pytest.mark.asyncio
async def test_add_book_returns_existing_item_when_already_in_library(make_book, make_library_item) -> None:
    book = make_book(id=5)
    existing_item = make_library_item(book=book, book_id=book.id)
    library_repository = SimpleNamespace(
        get_for_user_and_book=AsyncMock(return_value=existing_item),
        create_with_metadata=AsyncMock(),
    )
    book_repository = SimpleNamespace(upsert_from_google_payload=AsyncMock(return_value=book))
    service = LibraryService(library_repository, book_repository)

    result = await service.add_book(
        1,
        LibraryItemCreate(google_book_id="g-1", title="Testing Handbook"),
    )

    assert result is existing_item
    library_repository.create_with_metadata.assert_not_called()


@pytest.mark.asyncio
async def test_add_book_creates_item_with_extracted_metadata(make_book, make_library_item) -> None:
    book = make_book(id=9)
    created_item = make_library_item(book=book, book_id=book.id)
    library_repository = SimpleNamespace(
        get_for_user_and_book=AsyncMock(return_value=None),
        create_with_metadata=AsyncMock(return_value=created_item),
    )
    book_repository = SimpleNamespace(upsert_from_google_payload=AsyncMock(return_value=book))
    service = LibraryService(library_repository, book_repository)
    payload = LibraryItemCreate(
        google_book_id="g-1",
        title="Testing Handbook",
        category="Fantasy",
        reading_status="reading",
        priority="high",
        reading_format="ebook",
        pages_total=500,
        pages_read=42,
        started_at=date(2026, 1, 2),
        personal_notes="Interesting",
        favorite=True,
        tags="magic, tests",
    )

    result = await service.add_book(3, payload)

    assert result is created_item
    book_repository.upsert_from_google_payload.assert_awaited_once()
    create_kwargs = library_repository.create_with_metadata.await_args.kwargs
    assert create_kwargs["user_id"] == 3
    assert create_kwargs["metadata"]["category"] == "Fantasy"
    assert create_kwargs["metadata"]["reading_status"] == "reading"
    assert create_kwargs["metadata"]["favorite"] is True


@pytest.mark.asyncio
async def test_update_book_raises_not_found_when_item_is_missing() -> None:
    library_repository = SimpleNamespace(get_for_user_and_book=AsyncMock(return_value=None))
    service = LibraryService(library_repository, SimpleNamespace())

    with pytest.raises(HTTPException) as exc:
        await service.update_book(1, 99, LibraryItemUpdate(priority="high"))

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_book_requires_finished_at_for_finished_status() -> None:
    existing = SimpleNamespace(pages_total=200, pages_read=10)
    library_repository = SimpleNamespace(get_for_user_and_book=AsyncMock(return_value=existing))
    service = LibraryService(library_repository, SimpleNamespace())

    with pytest.raises(HTTPException) as exc:
        await service.update_book(1, 7, LibraryItemUpdate(reading_status="finished"))

    assert exc.value.status_code == 400
    assert "date de fin" in exc.value.detail


@pytest.mark.asyncio
async def test_update_book_rejects_pages_read_above_existing_total() -> None:
    existing = SimpleNamespace(pages_total=100, pages_read=50)
    library_repository = SimpleNamespace(get_for_user_and_book=AsyncMock(return_value=existing))
    service = LibraryService(library_repository, SimpleNamespace())

    with pytest.raises(HTTPException) as exc:
        await service.update_book(1, 7, LibraryItemUpdate(pages_read=120))

    assert exc.value.status_code == 400
    assert "pages lues" in exc.value.detail


@pytest.mark.asyncio
async def test_update_book_clears_finished_date_when_status_changes(make_library_item) -> None:
    existing = make_library_item(reading_status="finished", finished_at=date(2026, 2, 3), pages_total=300, pages_read=280)
    updated_item = make_library_item(reading_status="reading", finished_at=None)
    library_repository = SimpleNamespace(
        get_for_user_and_book=AsyncMock(return_value=existing),
        update=AsyncMock(return_value=updated_item),
    )
    service = LibraryService(library_repository, SimpleNamespace())

    result = await service.update_book(1, existing.book_id, LibraryItemUpdate(reading_status="reading"))

    assert result is updated_item
    assert library_repository.update.await_args.args[1]["finished_at"] is None


@pytest.mark.asyncio
async def test_update_book_rejects_pages_total_below_pages_read(make_library_item) -> None:
    existing = make_library_item(pages_total=300, pages_read=150)
    library_repository = SimpleNamespace(get_for_user_and_book=AsyncMock(return_value=existing))
    service = LibraryService(library_repository, SimpleNamespace())

    with pytest.raises(HTTPException) as exc:
        await service.update_book(1, existing.book_id, LibraryItemUpdate(pages_total=100))

    assert exc.value.status_code == 400
    assert "pages lues" in exc.value.detail


@pytest.mark.asyncio
async def test_remove_book_deletes_existing_item(make_library_item) -> None:
    existing = make_library_item()
    library_repository = SimpleNamespace(
        get_for_user_and_book=AsyncMock(return_value=existing),
        delete_for_user_and_book=AsyncMock(),
    )
    service = LibraryService(library_repository, SimpleNamespace())

    await service.remove_book(1, existing.book_id)

    library_repository.delete_for_user_and_book.assert_awaited_once_with(1, existing.book_id)


@pytest.mark.asyncio
async def test_remove_book_raises_not_found_when_item_is_missing() -> None:
    library_repository = SimpleNamespace(get_for_user_and_book=AsyncMock(return_value=None))
    service = LibraryService(library_repository, SimpleNamespace())

    with pytest.raises(HTTPException) as exc:
        await service.remove_book(1, 999)

    assert exc.value.status_code == 404
