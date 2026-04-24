from datetime import date
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.schemas.dashboard import DashboardGoalUpdate
from app.services.dashboard.dashboard_service import DashboardService


@pytest.mark.asyncio
async def test_get_overview_computes_dashboard_metrics(make_book, make_library_item, make_review, make_user) -> None:
    current_year = date.today().year
    user = make_user(reading_goal=10)
    finished_book = make_book(id=1, title="Finished Book")
    reading_book = make_book(id=2, title="Reading Book")
    dnf_book = make_book(id=3, title="Dropped Book")

    library_items = [
        make_library_item(
            book=finished_book,
            book_id=finished_book.id,
            reading_status="finished",
            favorite=True,
            category="Fantasy",
            priority="high",
            tags="epic, magic",
            finished_at=date(current_year, 3, 10),
            reading_format="paper",
        ),
        make_library_item(
            id=2,
            book=reading_book,
            book_id=reading_book.id,
            reading_status="reading",
            category="Fantasy",
            priority="medium",
            tags="magic",
            reading_format="ebook",
        ),
        make_library_item(
            id=3,
            book=dnf_book,
            book_id=dnf_book.id,
            reading_status="dnf",
            category="Essay",
            priority="low",
            tags="analysis",
            reading_format="paper",
        ),
    ]
    reviews = [
        make_review(rating=5, book=finished_book, book_id=finished_book.id),
        make_review(id=2, rating=3, book=reading_book, book_id=reading_book.id),
    ]

    library_repository = SimpleNamespace(list_for_user=AsyncMock(return_value=library_items))
    review_repository = SimpleNamespace(list_for_user=AsyncMock(return_value=reviews))
    user_repository = SimpleNamespace(update_reading_goal=AsyncMock())
    service = DashboardService(library_repository, review_repository, user_repository)

    overview = await service.get_overview(user)

    assert overview.books_in_library == 3
    assert overview.books_read_this_year == 1
    assert overview.books_in_progress == 1
    assert overview.books_to_read == 0
    assert overview.books_dnf == 1
    assert overview.favorite_books == 1
    assert overview.completion_rate == 33
    assert overview.average_rating == 4.0
    assert overview.reading_goal_progress == 10
    assert {metric.label: metric.value for metric in overview.categories} == {"Fantasy": 2, "Essay": 1}
    assert {metric.label: metric.value for metric in overview.top_tags} == {"magic": 2, "epic": 1, "analysis": 1}


@pytest.mark.asyncio
async def test_update_goal_persists_goal_and_returns_fresh_overview(make_user) -> None:
    user = make_user(reading_goal=12)
    library_repository = SimpleNamespace(list_for_user=AsyncMock(return_value=[]))
    review_repository = SimpleNamespace(list_for_user=AsyncMock(return_value=[]))
    user_repository = SimpleNamespace(update_reading_goal=AsyncMock())
    service = DashboardService(library_repository, review_repository, user_repository)
    expected = SimpleNamespace(books_in_library=0)
    service.get_overview = AsyncMock(return_value=expected)

    result = await service.update_goal(user, DashboardGoalUpdate(reading_goal=30))

    user_repository.update_reading_goal.assert_awaited_once_with(user, 30)
    assert result is expected
