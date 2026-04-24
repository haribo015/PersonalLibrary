from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi import HTTPException

from app.services.books.google_books_service import GoogleBooksService


class FakeResponse:
    def __init__(self, payload: dict, *, status_code: int = 200) -> None:
        self._payload = payload
        self.status_code = status_code
        self.request = httpx.Request("GET", "https://example.com")

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "request failed",
                request=self.request,
                response=httpx.Response(self.status_code, request=self.request),
            )


class FakeAsyncClient:
    def __init__(self, responses_or_errors: list[object]) -> None:
        self.responses_or_errors = responses_or_errors
        self.calls: list[tuple[str, dict]] = []

    async def __aenter__(self) -> FakeAsyncClient:
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        return None

    async def get(self, url: str, params: dict | None = None):
        self.calls.append((url, params or {}))
        outcome = self.responses_or_errors.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


@pytest.mark.asyncio
async def test_search_books_normalizes_results_and_marks_saved_items(monkeypatch) -> None:
    fake_client = FakeAsyncClient(
        [
            FakeResponse(
                {
                    "items": [
                        {
                            "id": "g-1",
                            "volumeInfo": {
                                "title": "Testing Handbook",
                                "authors": ["Alice"],
                                "description": "Handbook",
                                "publishedDate": "2024",
                                "imageLinks": {"thumbnail": "http://example.com/1.jpg"},
                                "ratingsCount": 2,
                            },
                        },
                        {
                            "id": "g-1",
                            "volumeInfo": {
                                "title": "Testing Handbook",
                                "authors": ["Alice"],
                                "description": "Improved",
                                "publishedDate": "2024",
                                "imageLinks": {"thumbnail": "http://example.com/2.jpg"},
                                "ratingsCount": 10,
                            },
                        },
                        {
                            "id": "g-2",
                            "volumeInfo": {
                                "title": "Other Book",
                                "authors": ["Bob"],
                                "ratingsCount": 1,
                            },
                        },
                    ]
                }
            )
        ]
    )
    monkeypatch.setattr(
        "app.services.books.google_books_service.httpx.AsyncClient",
        lambda timeout: fake_client,
    )
    library_repository = SimpleNamespace(
        list_for_user=AsyncMock(return_value=[SimpleNamespace(book=SimpleNamespace(google_book_id="g-2"))])
    )

    results = await GoogleBooksService().search_books(
        "  testing   handbook ",
        library_repository=library_repository,
        user_id=1,
    )

    assert [book.google_book_id for book in results] == ["g-1", "g-2"]
    assert results[0].cover_image == "https://example.com/2.jpg"
    assert results[1].already_in_library is True
    assert fake_client.calls[0][1]["q"] == "testing handbook"


@pytest.mark.asyncio
async def test_search_books_returns_empty_list_for_blank_query() -> None:
    results = await GoogleBooksService().search_books("   ")

    assert results == []


@pytest.mark.asyncio
async def test_search_books_retries_after_transient_http_status_error(monkeypatch) -> None:
    fake_client = FakeAsyncClient(
        [
            FakeResponse({}, status_code=503),
            FakeResponse({"items": [{"id": "g-1", "volumeInfo": {"title": "Recovered"}}]}),
        ]
    )
    monkeypatch.setattr(
        "app.services.books.google_books_service.httpx.AsyncClient",
        lambda timeout: fake_client,
    )

    results = await GoogleBooksService().search_books("Recovered")

    assert [book.google_book_id for book in results] == ["g-1"]
    assert len(fake_client.calls) == 2


@pytest.mark.asyncio
async def test_search_books_raises_service_unavailable_after_retries(monkeypatch) -> None:
    fake_client = FakeAsyncClient(
        [
            httpx.ConnectError("network down"),
            httpx.ConnectError("network down"),
            httpx.ConnectError("network down"),
        ]
    )
    monkeypatch.setattr(
        "app.services.books.google_books_service.httpx.AsyncClient",
        lambda timeout: fake_client,
    )

    with pytest.raises(HTTPException) as exc:
        await GoogleBooksService().search_books("testing")

    assert exc.value.status_code == 503
    assert "indisponible" in exc.value.detail


@pytest.mark.asyncio
async def test_get_book_details_returns_google_metadata(monkeypatch) -> None:
    fake_client = FakeAsyncClient(
        [
            FakeResponse(
                {
                    "volumeInfo": {
                        "subtitle": "Deep dive",
                        "publisher": "Example Press",
                        "pageCount": 456,
                        "categories": ["Testing", "Engineering"],
                        "language": "fr",
                        "averageRating": 4.5,
                        "ratingsCount": 120,
                        "previewLink": "https://example.com/preview",
                        "infoLink": "https://example.com/info",
                        "maturityRating": "NOT_MATURE",
                    }
                }
            )
        ]
    )
    monkeypatch.setattr(
        "app.services.books.google_books_service.httpx.AsyncClient",
        lambda timeout: fake_client,
    )

    details = await GoogleBooksService().get_book_details("google-1")

    assert details is not None
    assert details.publisher == "Example Press"
    assert details.categories == ["Testing", "Engineering"]
    assert details.preview_link == "https://example.com/preview"


@pytest.mark.asyncio
async def test_get_book_details_returns_none_on_404(monkeypatch) -> None:
    fake_client = FakeAsyncClient([FakeResponse({}, status_code=404)])
    monkeypatch.setattr(
        "app.services.books.google_books_service.httpx.AsyncClient",
        lambda timeout: fake_client,
    )

    details = await GoogleBooksService().get_book_details("missing")

    assert details is None


@pytest.mark.asyncio
async def test_get_book_details_retries_then_succeeds(monkeypatch) -> None:
    fake_client = FakeAsyncClient(
        [
            FakeResponse({}, status_code=503),
            FakeResponse({"volumeInfo": {"publisher": "Recovered Press"}}),
        ]
    )
    monkeypatch.setattr(
        "app.services.books.google_books_service.httpx.AsyncClient",
        lambda timeout: fake_client,
    )

    details = await GoogleBooksService().get_book_details("google-1")

    assert details is not None
    assert details.publisher == "Recovered Press"
    assert len(fake_client.calls) == 2


@pytest.mark.asyncio
async def test_get_book_details_returns_none_after_network_retries(monkeypatch) -> None:
    fake_client = FakeAsyncClient(
        [
            httpx.ConnectError("network down"),
            httpx.ConnectError("network down"),
            httpx.ConnectError("network down"),
        ]
    )
    monkeypatch.setattr(
        "app.services.books.google_books_service.httpx.AsyncClient",
        lambda timeout: fake_client,
    )

    details = await GoogleBooksService().get_book_details("google-1")

    assert details is None


@pytest.mark.asyncio
async def test_get_book_by_id_returns_book_payload(monkeypatch) -> None:
    fake_client = FakeAsyncClient(
        [
            FakeResponse(
                {
                    "volumeInfo": {
                        "title": "API Design",
                        "authors": ["Alice", "Bob"],
                        "description": "Design APIs",
                        "publishedDate": "2025-01-01",
                        "imageLinks": {"thumbnail": "http://example.com/cover.jpg"},
                    }
                }
            )
        ]
    )
    monkeypatch.setattr(
        "app.services.books.google_books_service.httpx.AsyncClient",
        lambda timeout: fake_client,
    )

    book = await GoogleBooksService().get_book_by_id("google-1")

    assert book is not None
    assert book.title == "API Design"
    assert book.authors == "Alice, Bob"
    assert book.cover_image == "https://example.com/cover.jpg"


@pytest.mark.asyncio
async def test_get_book_by_id_returns_none_on_404(monkeypatch) -> None:
    fake_client = FakeAsyncClient([FakeResponse({}, status_code=404)])
    monkeypatch.setattr(
        "app.services.books.google_books_service.httpx.AsyncClient",
        lambda timeout: fake_client,
    )

    book = await GoogleBooksService().get_book_by_id("missing")

    assert book is None


@pytest.mark.asyncio
async def test_get_book_by_id_retries_then_returns_payload(monkeypatch) -> None:
    fake_client = FakeAsyncClient(
        [
            FakeResponse({}, status_code=503),
            FakeResponse({"volumeInfo": {"title": "Recovered Book"}}),
        ]
    )
    monkeypatch.setattr(
        "app.services.books.google_books_service.httpx.AsyncClient",
        lambda timeout: fake_client,
    )

    book = await GoogleBooksService().get_book_by_id("google-1")

    assert book is not None
    assert book.title == "Recovered Book"
    assert len(fake_client.calls) == 2
