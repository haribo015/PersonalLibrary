from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_db
from app.repositories.library.library_repository import LibraryRepository
from app.repositories.reviews.review_repository import ReviewRepository
from app.routes.api_v1.dependencies import get_current_active_user
from app.schemas.books import GoogleBookSearchResult
from app.services.books.google_books_service import GoogleBooksService
from app.services.recommendations.recommendation_service import RecommendationService

router = APIRouter()


@router.get("/", response_model=list[GoogleBookSearchResult])
async def get_recommendations(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    service = RecommendationService(LibraryRepository(db), ReviewRepository(db), GoogleBooksService())
    return await service.get_recommendations(current_user.id)
