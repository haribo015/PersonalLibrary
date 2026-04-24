from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException

from app.schemas.reviews import ReviewUpsert
from app.services.reviews.review_service import ReviewService


@pytest.mark.asyncio
async def test_upsert_review_rejects_missing_book() -> None:
    service = ReviewService(
        review_repository=SimpleNamespace(),
        library_repository=SimpleNamespace(),
        book_repository=SimpleNamespace(get_by_id=AsyncMock(return_value=None)),
    )

    with pytest.raises(HTTPException) as exc:
        await service.upsert_review(1, ReviewUpsert(book_id=12, rating=5, comment="Great"))

    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_upsert_review_requires_book_in_user_library(make_book) -> None:
    service = ReviewService(
        review_repository=SimpleNamespace(),
        library_repository=SimpleNamespace(get_for_user_and_book=AsyncMock(return_value=None)),
        book_repository=SimpleNamespace(get_by_id=AsyncMock(return_value=make_book(id=12))),
    )

    with pytest.raises(HTTPException) as exc:
        await service.upsert_review(1, ReviewUpsert(book_id=12, rating=5, comment="Great"))

    assert exc.value.status_code == 400
    assert "bibliotheque" in exc.value.detail


@pytest.mark.asyncio
async def test_upsert_review_persists_review_when_book_is_available(make_book, make_library_item, make_review) -> None:
    book = make_book(id=12)
    library_item = make_library_item(book=book, book_id=book.id)
    review = make_review(book=book, book_id=book.id)
    review_repository = SimpleNamespace(upsert=AsyncMock(return_value=review))
    service = ReviewService(
        review_repository=review_repository,
        library_repository=SimpleNamespace(get_for_user_and_book=AsyncMock(return_value=library_item)),
        book_repository=SimpleNamespace(get_by_id=AsyncMock(return_value=book)),
    )

    result = await service.upsert_review(3, ReviewUpsert(book_id=12, rating=4, comment="Solid"))

    assert result is review
    review_repository.upsert.assert_awaited_once_with(user_id=3, book_id=12, rating=4, comment="Solid")


@pytest.mark.asyncio
async def test_list_reviews_delegates_to_repository(make_review) -> None:
    expected_reviews = [make_review()]
    review_repository = SimpleNamespace(list_for_user=AsyncMock(return_value=expected_reviews))
    service = ReviewService(review_repository, SimpleNamespace(), SimpleNamespace())

    result = await service.list_reviews(5)

    assert result == expected_reviews
