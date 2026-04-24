from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.routes.api_v1.dependencies import get_current_active_user
from app.routes.api_v1.reviews import router as reviews_router_module
from app.schemas.reviews import UserBookReviewRead


def test_upsert_review_returns_review(build_client, monkeypatch, make_user, make_review) -> None:
    review = UserBookReviewRead.model_validate(make_review())
    service = SimpleNamespace(upsert_review=AsyncMock(return_value=review))
    monkeypatch.setattr(reviews_router_module, "ReviewService", lambda *args: service)
    client = build_client(
        reviews_router_module.router,
        prefix="/api/v1/reviews",
        dependency_overrides={get_current_active_user: lambda: make_user()},
    )

    response = client.post("/api/v1/reviews/", json={"book_id": 1, "rating": 5, "comment": "Great"})

    assert response.status_code == 200
    assert response.json()["rating"] == 5


def test_list_reviews_returns_review_history(build_client, monkeypatch, make_user, make_review) -> None:
    review = UserBookReviewRead.model_validate(make_review())
    service = SimpleNamespace(list_reviews=AsyncMock(return_value=[review]))
    monkeypatch.setattr(reviews_router_module, "ReviewService", lambda *args: service)
    client = build_client(
        reviews_router_module.router,
        prefix="/api/v1/reviews",
        dependency_overrides={get_current_active_user: lambda: make_user()},
    )

    response = client.get("/api/v1/reviews/")

    assert response.status_code == 200
    assert response.json()[0]["book"]["google_book_id"] == review.book.google_book_id
