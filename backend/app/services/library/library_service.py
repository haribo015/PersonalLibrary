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
        metadata = self._extract_metadata(payload)
        # Store the shared Google Books payload once, then attach user-specific
        # reading metadata through the library item.
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
        self._validate_reading_status(payload)
        self._validate_page_progress(existing, payload)

        return await self.library_repository.update(existing, payload)

    async def remove_book(self, user_id: int, book_id: int) -> None:
        existing = await self.library_repository.get_for_user_and_book(user_id, book_id)
        if existing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Livre introuvable dans la bibliotheque")
        await self.library_repository.delete_for_user_and_book(user_id, book_id)

    @staticmethod
    def _extract_metadata(payload: dict) -> dict:
        metadata_keys = {
            "category",
            "reading_status",
            "priority",
            "source",
            "reading_format",
            "pages_total",
            "pages_read",
            "started_at",
            "finished_at",
            "last_opened_at",
            "personal_notes",
            "favorite",
            "tags",
        }
        return {key: payload.pop(key) for key in metadata_keys}

    @staticmethod
    def _validate_reading_status(payload: dict) -> None:
        reading_status = payload.get("reading_status")
        if reading_status is None:
            return
        if reading_status not in {"finished", "dnf"}:
            # Non-terminal statuses should not keep an outdated completion date.
            payload.setdefault("finished_at", None)
            return
        if reading_status == "finished" and "finished_at" not in payload:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La date de fin est requise pour un livre lu")

    @staticmethod
    def _validate_page_progress(existing, payload: dict) -> None:
        pages_read = payload.get("pages_read")
        if pages_read is not None and "pages_total" not in payload:
            # Partial updates must still be validated against the stored total.
            LibraryService._ensure_pages_read_within_limit(pages_read, existing.pages_total)

        pages_total = payload.get("pages_total")
        if pages_total is not None:
            current_pages_read = pages_read if pages_read is not None else existing.pages_read
            LibraryService._ensure_pages_read_within_limit(current_pages_read, pages_total)

    @staticmethod
    def _ensure_pages_read_within_limit(pages_read: int | None, pages_total: int | None) -> None:
        if pages_total is not None and pages_read is not None and pages_read > pages_total:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Les pages lues ne peuvent pas depasser le total")
