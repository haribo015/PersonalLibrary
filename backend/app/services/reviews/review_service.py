from fastapi import HTTPException, status

from app.repositories.books.book_repository import BookRepository
from app.repositories.library.library_repository import LibraryRepository
from app.repositories.reviews.review_repository import ReviewRepository
from app.schemas.reviews import ReviewUpsert


class ReviewService:
    def __init__(
        self,
        review_repository: ReviewRepository,
        library_repository: LibraryRepository,
        book_repository: BookRepository,
    ) -> None:
        self.review_repository = review_repository
        self.library_repository = library_repository
        self.book_repository = book_repository

    async def upsert_review(self, user_id: int, review_in: ReviewUpsert):
        book = await self.book_repository.get_by_id(review_in.book_id)
        if book is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livre introuvable")

        library_item = await self.library_repository.get_for_user_and_book(user_id, review_in.book_id)
        if library_item is None:
            # A review is personal library metadata; requiring a saved book keeps
            # recommendations and dashboard metrics anchored to owned data.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ajoutez d'abord ce livre a votre bibliotheque personnelle",
            )

        return await self.review_repository.upsert(
            user_id=user_id,
            book_id=review_in.book_id,
            rating=review_in.rating,
            comment=review_in.comment,
        )

    async def list_reviews(self, user_id: int):
        return await self.review_repository.list_for_user(user_id)
