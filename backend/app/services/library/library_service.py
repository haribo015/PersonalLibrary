from fastapi import HTTPException, status

from app.repositories.books.book_repository import BookRepository
from app.repositories.library.library_repository import LibraryRepository
from app.schemas.library import LibraryItemCreate, LibraryItemUpdate


class LibraryService:
    def __init__(self, library_repository: LibraryRepository, book_repository: BookRepository) -> None:
        self.library_repository = library_repository
        self.book_repository = book_repository

    async def list_library(self, user_id: int):
        return await self.library_repository.list_for_user(user_id)

    async def add_book(self, user_id: int, book_in: LibraryItemCreate):
        payload = book_in.model_dump()
        metadata = {
            "category": payload.pop("category"),
            "reading_status": payload.pop("reading_status"),
            "priority": payload.pop("priority"),
            "source": payload.pop("source"),
            "reading_format": payload.pop("reading_format"),
            "pages_total": payload.pop("pages_total"),
            "pages_read": payload.pop("pages_read"),
            "started_at": payload.pop("started_at"),
            "finished_at": payload.pop("finished_at"),
            "last_opened_at": payload.pop("last_opened_at"),
            "personal_notes": payload.pop("personal_notes"),
            "favorite": payload.pop("favorite"),
            "tags": payload.pop("tags"),
        }
        book = await self.book_repository.upsert_from_google_payload(**payload)
        existing = await self.library_repository.get_for_user_and_book(user_id, book.id)
        if existing is not None:
            return existing
        return await self.library_repository.create_with_metadata(user_id=user_id, book=book, metadata=metadata)

    async def update_book(self, user_id: int, book_id: int, update_in: LibraryItemUpdate):
        existing = await self.library_repository.get_for_user_and_book(user_id, book_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livre introuvable dans la bibliotheque")

        payload = update_in.model_dump(exclude_unset=True)
        if "reading_status" in payload:
            if payload["reading_status"] not in {"finished", "dnf"}:
                payload.setdefault("finished_at", None)
            if payload["reading_status"] == "finished" and "finished_at" not in payload:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La date de fin est requise pour un livre lu")

        if "pages_read" in payload and "pages_total" not in payload:
            pages_total = existing.pages_total
            if pages_total is not None and payload["pages_read"] is not None and payload["pages_read"] > pages_total:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Les pages lues ne peuvent pas depasser le total")

        if "pages_total" in payload and payload["pages_total"] is not None:
            pages_read = payload.get("pages_read", existing.pages_read)
            if pages_read is not None and pages_read > payload["pages_total"]:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Les pages lues ne peuvent pas depasser le total")

        return await self.library_repository.update(existing, payload)

    async def remove_book(self, user_id: int, book_id: int) -> None:
        existing = await self.library_repository.get_for_user_and_book(user_id, book_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livre introuvable dans la bibliotheque")
        await self.library_repository.delete_for_user_and_book(user_id, book_id)
