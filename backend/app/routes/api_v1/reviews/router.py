from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_db
from app.repositories.books.book_repository import BookRepository
from app.repositories.library.library_repository import LibraryRepository
from app.repositories.reviews.review_repository import ReviewRepository
from app.routes.api_v1.dependencies import get_current_active_user
from app.schemas.reviews import ReviewUpsert, UserBookReviewRead
from app.services.reviews.review_service import ReviewService

router = APIRouter()


@router.post("/", response_model=UserBookReviewRead)
async def upsert_review(
    review_in: ReviewUpsert,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    # Reviews are scoped to the authenticated user; the service verifies the book
    # belongs to that user's library before accepting the note.
    service = ReviewService(ReviewRepository(db), LibraryRepository(db), BookRepository(db))
    return await service.upsert_review(current_user.id, review_in)


@router.get("/", response_model=list[UserBookReviewRead])
async def list_reviews(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    service = ReviewService(ReviewRepository(db), LibraryRepository(db), BookRepository(db))
    return await service.list_reviews(current_user.id)
