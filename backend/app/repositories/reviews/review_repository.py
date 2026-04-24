from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.models import BookReview


class ReviewRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_for_user_and_book(self, user_id: int, book_id: int) -> BookReview | None:
        result = await self.db.execute(
            select(BookReview)
            .where(BookReview.user_id == user_id, BookReview.book_id == book_id)
            .options(selectinload(BookReview.book))
        )
        return result.scalar_one_or_none()

    async def list_for_user(self, user_id: int) -> list[BookReview]:
        result = await self.db.execute(
            select(BookReview)
            .where(BookReview.user_id == user_id)
            .options(selectinload(BookReview.book))
            .order_by(BookReview.created_at.desc())
        )
        return list(result.scalars().unique().all())

    async def upsert(
        self,
        *,
        user_id: int,
        book_id: int,
        rating: int,
        comment: str | None,
    ) -> BookReview:
        review = await self.get_for_user_and_book(user_id, book_id)
        if review is None:
            review = BookReview(user_id=user_id, book_id=book_id, rating=rating, comment=comment)
            self.db.add(review)
        else:
            review.rating = rating
            review.comment = comment
        await self.db.commit()
        result = await self.db.execute(
            select(BookReview)
            .where(BookReview.user_id == user_id, BookReview.book_id == book_id)
            .options(selectinload(BookReview.book))
        )
        return result.scalar_one()
