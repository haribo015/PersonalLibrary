from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import Book, BookReview, LibraryItem


class LibraryRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_for_user(self, user_id: int) -> list[LibraryItem]:
        result = await self.db.execute(
            select(LibraryItem)
            .where(LibraryItem.user_id == user_id)
            .options(
                # Eager-load books to avoid async lazy-loading surprises during
                # response serialization and dashboard/recommendation aggregation.
                selectinload(LibraryItem.book),
            )
            .order_by(LibraryItem.created_at.desc())
        )
        return list(result.scalars().unique().all())

    async def get_for_user_and_book(self, user_id: int, book_id: int) -> LibraryItem | None:
        result = await self.db.execute(
            select(LibraryItem)
            .where(LibraryItem.user_id == user_id, LibraryItem.book_id == book_id)
            .options(selectinload(LibraryItem.book))
        )
        return result.scalar_one_or_none()

    async def create(self, *, user_id: int, book: Book) -> LibraryItem:
        item = LibraryItem(user_id=user_id, book_id=book.id)
        self.db.add(item)
        await self.db.commit()
        return await self.get_for_user_and_book(user_id, book.id)  # type: ignore[return-value]

    async def create_with_metadata(self, *, user_id: int, book: Book, metadata: dict) -> LibraryItem:
        item = LibraryItem(user_id=user_id, book_id=book.id, **metadata)
        self.db.add(item)
        await self.db.commit()
        return await self.get_for_user_and_book(user_id, book.id)  # type: ignore[return-value]

    async def update(self, item: LibraryItem, payload: dict) -> LibraryItem:
        for key, value in payload.items():
            setattr(item, key, value)
        await self.db.commit()
        await self.db.refresh(item)
        return item

    async def delete_for_user_and_book(self, user_id: int, book_id: int) -> None:
        # Removing a book from a personal library also removes the user's review
        # for that book, keeping derived dashboard metrics consistent.
        await self.db.execute(delete(LibraryItem).where(LibraryItem.user_id == user_id, LibraryItem.book_id == book_id))
        await self.db.execute(delete(BookReview).where(BookReview.user_id == user_id, BookReview.book_id == book_id))
        await self.db.commit()
