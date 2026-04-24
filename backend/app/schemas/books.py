from pydantic import BaseModel, ConfigDict


class BookPayload(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    google_book_id: str
    title: str
    authors: str | None = None
    description: str | None = None
    cover_image: str | None = None
    published_date: str | None = None


class GoogleBookSearchResult(BookPayload):
    model_config = ConfigDict(from_attributes=True)

    already_in_library: bool = False


class GoogleBookDetails(BaseModel):
    subtitle: str | None = None
    publisher: str | None = None
    page_count: int | None = None
    categories: list[str] = []
    language: str | None = None
    average_rating: float | None = None
    ratings_count: int | None = None
    preview_link: str | None = None
    info_link: str | None = None
    maturity_rating: str | None = None
