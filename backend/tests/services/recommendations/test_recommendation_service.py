from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.schemas.books import GoogleBookSearchResult
from app.services.recommendations.recommendation_service import RecommendationService


@pytest.mark.asyncio
async def test_get_recommendations_uses_high_rated_reviews_as_seed_terms(make_book, make_review) -> None:
    liked_book = make_book(title="Pragmatic Testing Patterns", authors="Alice, Bob")
    reviews = [make_review(book=liked_book, book_id=liked_book.id, rating=5)]
    library_repository = SimpleNamespace(list_for_user=AsyncMock(return_value=[]))
    review_repository = SimpleNamespace(list_for_user=AsyncMock(return_value=reviews))
    google_books_service = SimpleNamespace(
        search_books=AsyncMock(
            return_value=[
                GoogleBookSearchResult(google_book_id="g-1", title="New Book"),
                GoogleBookSearchResult(google_book_id="g-2", title="Saved", already_in_library=True),
            ]
        )
    )
    service = RecommendationService(library_repository, review_repository, google_books_service)

    results = await service.get_recommendations(4, limit=5)

    query = google_books_service.search_books.await_args.args[0]
    assert "Alice" in query or "Bob" in query or "Pragmatic" in query
    assert [book.google_book_id for book in results] == ["g-1"]


@pytest.mark.asyncio
async def test_get_recommendations_falls_back_to_library_titles(make_book, make_library_item) -> None:
    library_items = [
        make_library_item(book=make_book(title="Distributed Systems Patterns"), book_id=1),
    ]
    library_repository = SimpleNamespace(list_for_user=AsyncMock(return_value=library_items))
    review_repository = SimpleNamespace(list_for_user=AsyncMock(return_value=[]))
    google_books_service = SimpleNamespace(
        search_books=AsyncMock(return_value=[GoogleBookSearchResult(google_book_id="g-1", title="Suggested")])
    )
    service = RecommendationService(library_repository, review_repository, google_books_service)

    await service.get_recommendations(9)

    query = google_books_service.search_books.await_args.args[0]
    assert "Distributed" in query


@pytest.mark.asyncio
async def test_get_recommendations_returns_empty_list_without_seed_terms() -> None:
    library_repository = SimpleNamespace(list_for_user=AsyncMock(return_value=[]))
    review_repository = SimpleNamespace(list_for_user=AsyncMock(return_value=[]))
    google_books_service = SimpleNamespace(search_books=AsyncMock())
    service = RecommendationService(library_repository, review_repository, google_books_service)

    results = await service.get_recommendations(2)

    assert results == []
    google_books_service.search_books.assert_not_called()
