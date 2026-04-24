from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.routes.api_v1.dependencies import get_current_active_user
from app.routes.api_v1.library import router as library_router_module
from app.schemas.library import LibraryItemRead


def test_list_library_returns_items(build_client, monkeypatch, make_user, make_library_item) -> None:
    item = LibraryItemRead.model_validate(make_library_item())
    service = SimpleNamespace(list_library=AsyncMock(return_value=[item]))
    monkeypatch.setattr(library_router_module, "LibraryService", lambda *args: service)
    client = build_client(
        library_router_module.router,
        prefix="/api/v1/library",
        dependency_overrides={get_current_active_user: lambda: make_user()},
    )

    response = client.get("/api/v1/library/")

    assert response.status_code == 200
    assert response.json()[0]["book"]["title"] == item.book.title


def test_add_book_to_library_returns_created_item(build_client, monkeypatch, make_user, make_library_item) -> None:
    item = LibraryItemRead.model_validate(make_library_item())
    service = SimpleNamespace(add_book=AsyncMock(return_value=item))
    monkeypatch.setattr(library_router_module, "LibraryService", lambda *args: service)
    client = build_client(
        library_router_module.router,
        prefix="/api/v1/library",
        dependency_overrides={get_current_active_user: lambda: make_user()},
    )

    response = client.post("/api/v1/library/", json={"google_book_id": "g-1", "title": "Testing Handbook"})

    assert response.status_code == 201
    assert response.json()["book_id"] == item.book_id


def test_update_library_book_returns_updated_item(build_client, monkeypatch, make_user, make_library_item) -> None:
    item = LibraryItemRead.model_validate(make_library_item(priority="high"))
    service = SimpleNamespace(update_book=AsyncMock(return_value=item))
    monkeypatch.setattr(library_router_module, "LibraryService", lambda *args: service)
    client = build_client(
        library_router_module.router,
        prefix="/api/v1/library",
        dependency_overrides={get_current_active_user: lambda: make_user()},
    )

    response = client.patch("/api/v1/library/1", json={"priority": "high"})

    assert response.status_code == 200
    assert response.json()["priority"] == "high"


def test_remove_book_from_library_returns_no_content(build_client, monkeypatch, make_user) -> None:
    service = SimpleNamespace(remove_book=AsyncMock(return_value=None))
    monkeypatch.setattr(library_router_module, "LibraryService", lambda *args: service)
    client = build_client(
        library_router_module.router,
        prefix="/api/v1/library",
        dependency_overrides={get_current_active_user: lambda: make_user()},
    )

    response = client.delete("/api/v1/library/5")

    assert response.status_code == 204
