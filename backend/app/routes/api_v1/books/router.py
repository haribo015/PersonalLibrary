from typing import Annotated, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_db
from app.repositories.books.book_repository import BookRepository
from app.repositories.library.library_repository import LibraryRepository
from app.repositories.reviews.review_repository import ReviewRepository
from app.routes.api_v1.dependencies import get_optional_current_user
from app.schemas.book_overview import BookOverview
from app.schemas.books import GoogleBookSearchResult
from app.services.books.google_books_service import GoogleBooksService

router = APIRouter()


@router.get("/search", response_model=list[GoogleBookSearchResult])
async def search_books(
    q: Annotated[str, Query(..., min_length=1)],
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_current_user)],
):
    library_repository = LibraryRepository(db)
    # Passing the user context lets the service flag books already saved without
    # making anonymous search depend on authentication.
    return await GoogleBooksService().search_books(
        q,
        library_repository=library_repository,
        user_id=current_user.id if current_user else None,
    )


@router.get("/{google_book_id}/overview", response_model=BookOverview)
async def get_book_overview(
    google_book_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[Optional[User], Depends(get_optional_current_user)],
):
    google_books_service = GoogleBooksService()
    book_repository = BookRepository(db)
    library_repository = LibraryRepository(db)
    review_repository = ReviewRepository(db)

    book = await book_repository.get_by_google_book_id(google_book_id)
    if book is None:
        # Detail pages may be opened from search results before the book is saved,
        # so Google Books is the fallback source of truth for the base payload.
        book = await google_books_service.get_book_by_id(google_book_id)
        if book is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livre introuvable")

    library_item = None
    review = None
    if current_user is not None and getattr(book, "id", None) is not None:
        library_item = await library_repository.get_for_user_and_book(current_user.id, book.id)
        review = await review_repository.get_for_user_and_book(current_user.id, book.id)

    google_details = await google_books_service.get_book_details(google_book_id)

    return BookOverview(book=book, google_details=google_details, library_item=library_item, review=review)
