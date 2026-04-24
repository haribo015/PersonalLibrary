from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Book


class BookRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, book_id: int) -> Book | None:
        result = await self.db.execute(select(Book).where(Book.id == book_id))
        return result.scalar_one_or_none()

    async def get_by_google_book_id(self, google_book_id: str) -> Book | None:
        result = await self.db.execute(select(Book).where(Book.google_book_id == google_book_id))
        return result.scalar_one_or_none()

    async def upsert_from_google_payload(
        self,
        *,
        google_book_id: str,
        title: str,
        authors: str | None,
        description: str | None,
        cover_image: str | None,
        published_date: str | None,
    ) -> Book:
        existing = await self.get_by_google_book_id(google_book_id)
        if existing is not None:
            existing.title = title
            existing.authors = authors
            existing.description = description
            existing.cover_image = cover_image
            existing.published_date = published_date
            await self.db.commit()
            await self.db.refresh(existing)
            return existing

        book = Book(
            google_book_id=google_book_id,
            title=title,
            authors=authors,
            description=description,
            cover_image=cover_image,
            published_date=published_date,
        )
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return book
