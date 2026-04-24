from pydantic import BaseModel

from app.schemas.books import BookPayload, GoogleBookDetails
from app.schemas.library import LibraryItemRead
from app.schemas.reviews import UserBookReviewRead


class BookOverview(BaseModel):
    book: BookPayload
    google_details: GoogleBookDetails | None = None
    library_item: LibraryItemRead | None = None
    review: UserBookReviewRead | None = None
