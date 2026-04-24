from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.routes.api_v1.dashboard import router as dashboard_router_module
from app.routes.api_v1.dependencies import get_current_active_user


def test_get_dashboard_returns_overview(build_client, monkeypatch, make_user) -> None:
    service = SimpleNamespace(
        get_overview=AsyncMock(
            return_value={
                "books_in_library": 3,
                "books_read_this_year": 1,
                "books_in_progress": 1,
                "books_to_read": 1,
                "books_dnf": 0,
                "favorite_books": 1,
                "completion_rate": 33,
                "average_rating": 4.5,
                "reading_goal": 12,
                "reading_goal_progress": 8,
                "categories": [{"label": "Fantasy", "value": 2}],
                "formats": [{"label": "paper", "value": 2}],
                "statuses": [{"label": "reading", "value": 1}],
                "priorities": [{"label": "high", "value": 1}],
                "top_tags": [{"label": "magic", "value": 2}],
            }
        )
    )
    monkeypatch.setattr(dashboard_router_module, "DashboardService", lambda *args: service)
    client = build_client(
        dashboard_router_module.router,
        prefix="/api/v1/dashboard",
        dependency_overrides={get_current_active_user: lambda: make_user()},
    )

    response = client.get("/api/v1/dashboard/")

    assert response.status_code == 200
    assert response.json()["books_in_library"] == 3


def test_update_reading_goal_returns_updated_overview(build_client, monkeypatch, make_user) -> None:
    service = SimpleNamespace(
        update_goal=AsyncMock(
            return_value={
                "books_in_library": 0,
                "books_read_this_year": 0,
                "books_in_progress": 0,
                "books_to_read": 0,
                "books_dnf": 0,
                "favorite_books": 0,
                "completion_rate": 0,
                "average_rating": 0.0,
                "reading_goal": 30,
                "reading_goal_progress": 0,
                "categories": [],
                "formats": [],
                "statuses": [],
                "priorities": [],
                "top_tags": [],
            }
        )
    )
    monkeypatch.setattr(dashboard_router_module, "DashboardService", lambda *args: service)
    client = build_client(
        dashboard_router_module.router,
        prefix="/api/v1/dashboard",
        dependency_overrides={get_current_active_user: lambda: make_user()},
    )

    response = client.patch("/api/v1/dashboard/goal", json={"reading_goal": 30})

    assert response.status_code == 200
    assert response.json()["reading_goal"] == 30
