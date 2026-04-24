from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from app.repositories.reviews.review_repository import ReviewRepository


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

    def scalar_one(self):
        return self.scalar

    def scalars(self):
        return FakeScalars(self.values)


@pytest.mark.asyncio
async def test_get_for_user_and_book_returns_scalar_result(make_review) -> None:
    review = make_review()
    db = SimpleNamespace(execute=AsyncMock(return_value=FakeExecuteResult(scalar=review)))

    result = await ReviewRepository(db).get_for_user_and_book(1, 1)

    assert result is review


@pytest.mark.asyncio
async def test_list_for_user_returns_reviews(make_review) -> None:
    reviews = [make_review(id=1), make_review(id=2, book_id=2)]
    db = SimpleNamespace(execute=AsyncMock(return_value=FakeExecuteResult(values=reviews)))

    result = await ReviewRepository(db).list_for_user(1)

    assert result == reviews


@pytest.mark.asyncio
async def test_upsert_creates_review_when_missing(make_review) -> None:
    review = make_review()
    db = SimpleNamespace(execute=AsyncMock(return_value=FakeExecuteResult(scalar=review)), commit=AsyncMock(), add=Mock())
    repository = ReviewRepository(db)
    repository.get_for_user_and_book = AsyncMock(return_value=None)

    result = await repository.upsert(user_id=1, book_id=3, rating=5, comment="Excellent")

    assert result is review
    created_review = db.add.call_args.args[0]
    assert created_review.rating == 5
    assert created_review.comment == "Excellent"
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_upsert_updates_existing_review(make_review) -> None:
    existing = make_review(rating=2, comment="Old")
    refreshed = make_review(rating=4, comment="Better")
    db = SimpleNamespace(execute=AsyncMock(return_value=FakeExecuteResult(scalar=refreshed)), commit=AsyncMock(), add=Mock())
    repository = ReviewRepository(db)
    repository.get_for_user_and_book = AsyncMock(return_value=existing)

    result = await repository.upsert(user_id=1, book_id=1, rating=4, comment="Better")

    assert result is refreshed
    assert existing.rating == 4
    assert existing.comment == "Better"
    db.add.assert_not_called()
    db.commit.assert_awaited_once()
