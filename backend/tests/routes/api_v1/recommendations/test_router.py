from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.routes.api_v1.dependencies import get_current_active_user
from app.routes.api_v1.recommendations import router as recommendations_router_module


def test_get_recommendations_returns_books(build_client, monkeypatch, make_user) -> None:
    service = SimpleNamespace(
        get_recommendations=AsyncMock(
            return_value=[
                {
                    "google_book_id": "g-1",
                    "title": "Suggested Book",
                    "authors": "Alice",
                    "description": "Suggestion",
                    "cover_image": None,
                    "published_date": "2025",
                    "already_in_library": False,
                }
            ]
        )
    )
    monkeypatch.setattr(recommendations_router_module, "RecommendationService", lambda *args: service)
    client = build_client(
        recommendations_router_module.router,
        prefix="/api/v1/recommendations",
        dependency_overrides={get_current_active_user: lambda: make_user()},
    )

    response = client.get("/api/v1/recommendations/")

    assert response.status_code == 200
    assert response.json()[0]["title"] == "Suggested Book"
