from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Callable

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from app.db.models import Book, BookReview, LibraryItem, User
from app.db.session import get_db


@pytest.fixture
def make_user() -> Callable[..., User]:
    def _make_user(**overrides: Any) -> User:
        data = {
            "id": 1,
            "email": "reader@example.com",
            "name": "Reader",
            "hashed_password": "hashed-password",
            "is_active": True,
            "reading_goal": 24,
        }
        data.update(overrides)
        return User(**data)

    return _make_user


@pytest.fixture
def make_book() -> Callable[..., Book]:
    def _make_book(**overrides: Any) -> Book:
        data = {
            "id": 1,
            "google_book_id": "google-1",
            "title": "The Testing Book",
            "authors": "Alice Example",
            "description": "A practical guide to testing.",
            "cover_image": "https://example.com/cover.jpg",
            "published_date": "2024-01-01",
        }
        data.update(overrides)
        return Book(**data)

    return _make_book


@pytest.fixture
def make_library_item(make_book: Callable[..., Book], make_user: Callable[..., User]) -> Callable[..., LibraryItem]:
    def _make_library_item(**overrides: Any) -> LibraryItem:
        user = overrides.pop("user", None) or make_user()
        book = overrides.pop("book", None) or make_book()
        data = {
            "id": 1,
            "user_id": user.id,
            "book_id": book.id,
            "category": "General",
            "reading_status": "to_read",
            "priority": "medium",
            "source": "manual",
            "reading_format": "paper",
            "pages_total": 320,
            "pages_read": 40,
            "started_at": None,
            "finished_at": None,
            "last_opened_at": None,
            "personal_notes": "A note",
            "favorite": False,
            "tags": "test, sample",
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        }
        data.update(overrides)
        item = LibraryItem(**data)
        item.user = user
        item.book = book
        return item

    return _make_library_item


@pytest.fixture
def make_review(make_book: Callable[..., Book], make_user: Callable[..., User]) -> Callable[..., BookReview]:
    def _make_review(**overrides: Any) -> BookReview:
        user = overrides.pop("user", None) or make_user()
        book = overrides.pop("book", None) or make_book()
        data = {
            "id": 1,
            "user_id": user.id,
            "book_id": book.id,
            "rating": 5,
            "comment": "Excellent read",
            "created_at": datetime(2026, 1, 1, tzinfo=timezone.utc),
        }
        data.update(overrides)
        review = BookReview(**data)
        review.user = user
        review.book = book
        return review

    return _make_review


@pytest.fixture
def build_client() -> Callable[..., TestClient]:
    clients: list[TestClient] = []

    def _build_client(
        router: APIRouter,
        *,
        prefix: str,
        dependency_overrides: dict[Callable[..., Any], Callable[..., Any]] | None = None,
    ) -> TestClient:
        app = FastAPI()
        app.include_router(router, prefix=prefix)

        async def override_get_db():
            yield object()

        app.dependency_overrides[get_db] = override_get_db
        if dependency_overrides:
            app.dependency_overrides.update(dependency_overrides)

        client = TestClient(app)
        clients.append(client)
        return client

    yield _build_client

    for client in clients:
        client.close()
