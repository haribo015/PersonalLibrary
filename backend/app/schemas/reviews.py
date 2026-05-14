from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.books import BookPayload


class ReviewUpsert(BaseModel):
    # Rating bounds are enforced at the API edge before service rules run.
    book_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = None


class UserBookReviewRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Include the book snapshot for dashboard/review screens without a second query.
    id: int
    user_id: int
    book_id: int
    rating: int
    comment: str | None = None
    created_at: datetime
    book: BookPayload
