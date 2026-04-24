from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_db
from app.repositories.books.book_repository import BookRepository
from app.repositories.library.library_repository import LibraryRepository
from app.routes.api_v1.dependencies import get_current_active_user
from app.schemas.library import LibraryItemCreate, LibraryItemRead, LibraryItemUpdate
from app.services.library.library_service import LibraryService

router = APIRouter()


@router.get("/", response_model=list[LibraryItemRead])
async def list_library(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = LibraryService(LibraryRepository(db), BookRepository(db))
    return await service.list_library(current_user.id)


@router.post("/", response_model=LibraryItemRead, status_code=status.HTTP_201_CREATED)
async def add_book_to_library(
    book_in: LibraryItemCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = LibraryService(LibraryRepository(db), BookRepository(db))
    return await service.add_book(current_user.id, book_in)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_book_from_library(
    book_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = LibraryService(LibraryRepository(db), BookRepository(db))
    await service.remove_book(current_user.id, book_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch("/{book_id}", response_model=LibraryItemRead)
async def update_library_book(
    book_id: int,
    update_in: LibraryItemUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    service = LibraryService(LibraryRepository(db), BookRepository(db))
    return await service.update_book(current_user.id, book_id, update_in)
