from __future__ import annotations

import asyncio
import re
from collections.abc import Iterable

import httpx
from fastapi import HTTPException, status

from app.core.config import settings
from app.repositories.library.library_repository import LibraryRepository
from app.schemas.books import BookPayload, GoogleBookDetails, GoogleBookSearchResult

GOOGLE_BOOKS_URL = "https://www.googleapis.com/books/v1/volumes"
WHITESPACE_RE = re.compile(r"\s+")


def _normalize_query(query: str) -> str:
    return WHITESPACE_RE.sub(" ", query).strip()


def _normalize_thumbnail(url: str | None) -> str | None:
    if not url:
        return None
    return url.replace("http://", "https://")


def _score_result(query: str, title: str, authors: Iterable[str], ratings_count: int | None) -> tuple[int, int]:
    lowered_query = query.lower()
    title_score = 2 if lowered_query in title.lower() else 0
    author_score = 1 if any(lowered_query in author.lower() for author in authors) else 0
    popularity = ratings_count or 0
    return (title_score + author_score, popularity)


class GoogleBooksService:
    async def search_books(
        self,
        query: str,
        *,
        max_results: int = 12,
        library_repository: LibraryRepository | None = None,
        user_id: int | None = None,
    ) -> list[GoogleBookSearchResult]:
        normalized_query = _normalize_query(query)
        if not normalized_query:
            return []

        params = {
            "q": normalized_query,
            "maxResults": max_results,
            "orderBy": "relevance",
            "printType": "books",
            "fields": (
                "items(id,volumeInfo/title,volumeInfo/authors,volumeInfo/description,"
                "volumeInfo/publishedDate,volumeInfo/imageLinks/thumbnail,"
                "volumeInfo/ratingsCount)"
            ),
        }
        if settings.google_books_api_key:
            params["key"] = settings.google_books_api_key

        data = None
        async with httpx.AsyncClient(timeout=10.0) as client:
            for attempt in range(3):
                try:
                    response = await client.get(GOOGLE_BOOKS_URL, params=params)
                    response.raise_for_status()
                    data = response.json()
                    break
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code in {429, 500, 502, 503, 504} and attempt < 2:
                        await asyncio.sleep(0.6 * (attempt + 1))
                        continue
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Google Books est temporairement indisponible. Reessayez dans quelques instants.",
                    ) from exc
                except httpx.HTTPError as exc:
                    if attempt < 2:
                        await asyncio.sleep(0.6 * (attempt + 1))
                        continue
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="La recherche Google Books est indisponible pour le moment.",
                    ) from exc

        if data is None:
            return []

        saved_google_ids: set[str] = set()
        if library_repository is not None and user_id is not None:
            saved_google_ids = {
                item.book.google_book_id for item in await library_repository.list_for_user(user_id)
            }

        deduped: dict[str, tuple[GoogleBookSearchResult, tuple[int, int]]] = {}
        for item in data.get("items", []):
            volume_info = item.get("volumeInfo", {})
            google_book_id = item.get("id", "")
            authors = volume_info.get("authors", [])
            result = GoogleBookSearchResult(
                google_book_id=google_book_id,
                title=volume_info.get("title", "Untitled"),
                authors=", ".join(authors) if authors else None,
                description=volume_info.get("description"),
                cover_image=_normalize_thumbnail(volume_info.get("imageLinks", {}).get("thumbnail")),
                published_date=volume_info.get("publishedDate"),
                already_in_library=google_book_id in saved_google_ids,
            )
            score = _score_result(normalized_query, result.title, authors, volume_info.get("ratingsCount"))
            previous = deduped.get(google_book_id)
            if previous is None or score > previous[1]:
                deduped[google_book_id] = (result, score)

        return [item for item, _ in sorted(deduped.values(), key=lambda entry: entry[1], reverse=True)]

    async def get_book_details(self, google_book_id: str) -> GoogleBookDetails | None:
        params = {
            "fields": (
                "volumeInfo/subtitle,volumeInfo/publisher,volumeInfo/pageCount,"
                "volumeInfo/categories,volumeInfo/language,volumeInfo/averageRating,"
                "volumeInfo/ratingsCount,volumeInfo/previewLink,volumeInfo/infoLink,"
                "volumeInfo/maturityRating"
            ),
        }
        if settings.google_books_api_key:
            params["key"] = settings.google_books_api_key

        async with httpx.AsyncClient(timeout=10.0) as client:
            for attempt in range(3):
                try:
                    response = await client.get(f"{GOOGLE_BOOKS_URL}/{google_book_id}", params=params)
                    response.raise_for_status()
                    volume_info = response.json().get("volumeInfo", {})
                    return GoogleBookDetails(
                        subtitle=volume_info.get("subtitle"),
                        publisher=volume_info.get("publisher"),
                        page_count=volume_info.get("pageCount"),
                        categories=volume_info.get("categories") or [],
                        language=volume_info.get("language"),
                        average_rating=volume_info.get("averageRating"),
                        ratings_count=volume_info.get("ratingsCount"),
                        preview_link=volume_info.get("previewLink"),
                        info_link=volume_info.get("infoLink"),
                        maturity_rating=volume_info.get("maturityRating"),
                    )
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                        return None
                    if exc.response.status_code in {429, 500, 502, 503, 504} and attempt < 2:
                        await asyncio.sleep(0.6 * (attempt + 1))
                        continue
                    return None
                except httpx.HTTPError:
                    if attempt < 2:
                        await asyncio.sleep(0.6 * (attempt + 1))
                        continue
                    return None

        return None

    async def get_book_by_id(self, google_book_id: str) -> BookPayload | None:
        params = {
            "fields": (
                "id,volumeInfo/title,volumeInfo/authors,volumeInfo/description,"
                "volumeInfo/publishedDate,volumeInfo/imageLinks/thumbnail"
            ),
        }
        if settings.google_books_api_key:
            params["key"] = settings.google_books_api_key

        async with httpx.AsyncClient(timeout=10.0) as client:
            for attempt in range(3):
                try:
                    response = await client.get(f"{GOOGLE_BOOKS_URL}/{google_book_id}", params=params)
                    response.raise_for_status()
                    volume_info = response.json().get("volumeInfo", {})
                    return BookPayload(
                        google_book_id=google_book_id,
                        title=volume_info.get("title", "Untitled"),
                        authors=", ".join(volume_info.get("authors", [])) if volume_info.get("authors") else None,
                        description=volume_info.get("description"),
                        cover_image=_normalize_thumbnail(volume_info.get("imageLinks", {}).get("thumbnail")),
                        published_date=volume_info.get("publishedDate"),
                    )
                except httpx.HTTPStatusError as exc:
                    if exc.response.status_code == status.HTTP_404_NOT_FOUND:
                        return None
                    if exc.response.status_code in {429, 500, 502, 503, 504} and attempt < 2:
                        await asyncio.sleep(0.6 * (attempt + 1))
                        continue
                    return None
                except httpx.HTTPError:
                    if attempt < 2:
                        await asyncio.sleep(0.6 * (attempt + 1))
                        continue
                    return None

        return None
