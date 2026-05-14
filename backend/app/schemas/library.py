from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.books import BookPayload


class LibraryItemCreate(BookPayload):
    # Creation combines the external book payload with the first set of personal metadata.
    category: str = "General"
    reading_status: str = "to_read"
    priority: str = "medium"
    source: str = "manual"
    reading_format: str = "paper"
    pages_total: int | None = Field(default=None, ge=0)
    pages_read: int | None = Field(default=None, ge=0)
    started_at: date | None = None
    finished_at: date | None = None
    last_opened_at: date | None = None
    personal_notes: str | None = None
    favorite: bool = False
    tags: str | None = None


class LibraryItemUpdate(BaseModel):
    # Partial update DTO: omitted fields keep their current database values.
    category: str | None = None
    reading_status: str | None = None
    priority: str | None = None
    source: str | None = None
    reading_format: str | None = None
    pages_total: int | None = Field(default=None, ge=0)
    pages_read: int | None = Field(default=None, ge=0)
    started_at: date | None = None
    finished_at: date | None = None
    last_opened_at: date | None = None
    personal_notes: str | None = None
    favorite: bool | None = None
    tags: str | None = None


class LibraryItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Read responses include the nested book to avoid extra frontend round trips.
    id: int
    user_id: int
    book_id: int
    category: str
    reading_status: str
    priority: str
    source: str
    reading_format: str
    pages_total: int | None = None
    pages_read: int | None = None
    started_at: date | None = None
    finished_at: date | None = None
    last_opened_at: date | None = None
    personal_notes: str | None = None
    favorite: bool
    tags: str | None = None
    created_at: datetime
    book: BookPayload
