from types import SimpleNamespace
from unittest.mock import AsyncMock

from app.routes.api_v1.books import router as books_router_module
from app.routes.api_v1.dependencies import get_optional_current_user


def test_search_books_returns_google_results_for_anonymous_user(build_client, monkeypatch) -> None:
    google_service = SimpleNamespace(
        search_books=AsyncMock(
            return_value=[
                {
                    "google_book_id": "g-1",
                    "title": "Testing Handbook",
                    "authors": "Alice",
                    "description": "Useful",
                    "cover_image": None,
                    "published_date": "2024",
                    "already_in_library": False,
                }
            ]
        )
    )
    monkeypatch.setattr(books_router_module, "GoogleBooksService", lambda: google_service)
    client = build_client(books_router_module.router, prefix="/api/v1/books")

    response = client.get("/api/v1/books/search?q=testing")

    assert response.status_code == 200
    assert response.json()[0]["google_book_id"] == "g-1"


def test_get_book_overview_returns_not_found_when_book_is_missing(build_client, monkeypatch) -> None:
    google_service = SimpleNamespace(
        get_book_by_id=AsyncMock(return_value=None),
        get_book_details=AsyncMock(return_value=None),
    )
    monkeypatch.setattr(books_router_module, "GoogleBooksService", lambda: google_service)
    monkeypatch.setattr(
        books_router_module,
        "BookRepository",
        lambda db: SimpleNamespace(get_by_google_book_id=AsyncMock(return_value=None)),
    )
    client = build_client(books_router_module.router, prefix="/api/v1/books")

    response = client.get("/api/v1/books/missing/overview")

    assert response.status_code == 404


def test_get_book_overview_returns_book_google_details_and_user_data(
    build_client,
    monkeypatch,
    make_book,
    make_library_item,
    make_review,
    make_user,
) -> None:
    user = make_user()
    book = make_book()
    library_item = make_library_item(book=book, book_id=book.id, user=user)
    review = make_review(book=book, book_id=book.id, user=user)
    google_service = SimpleNamespace(
        get_book_by_id=AsyncMock(return_value=None),
        get_book_details=AsyncMock(return_value={"publisher": "Example Press", "categories": ["Testing"]}),
    )
    monkeypatch.setattr(books_router_module, "GoogleBooksService", lambda: google_service)
    monkeypatch.setattr(
        books_router_module,
        "BookRepository",
        lambda db: SimpleNamespace(get_by_google_book_id=AsyncMock(return_value=book)),
    )
    monkeypatch.setattr(
        books_router_module,
        "LibraryRepository",
        lambda db: SimpleNamespace(get_for_user_and_book=AsyncMock(return_value=library_item)),
    )
    monkeypatch.setattr(
        books_router_module,
        "ReviewRepository",
        lambda db: SimpleNamespace(get_for_user_and_book=AsyncMock(return_value=review)),
    )
    client = build_client(
        books_router_module.router,
        prefix="/api/v1/books",
        dependency_overrides={get_optional_current_user: lambda: user},
    )

    response = client.get("/api/v1/books/google-1/overview")

    assert response.status_code == 200
    body = response.json()
    assert body["book"]["google_book_id"] == "google-1"
    assert body["google_details"]["publisher"] == "Example Press"
    assert body["library_item"]["book_id"] == book.id
    assert body["review"]["rating"] == review.rating
