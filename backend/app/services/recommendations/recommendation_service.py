from collections import Counter

from app.repositories.library.library_repository import LibraryRepository
from app.repositories.reviews.review_repository import ReviewRepository
from app.schemas.books import GoogleBookSearchResult
from app.services.books.google_books_service import GoogleBooksService


class RecommendationService:
    def __init__(
        self,
        library_repository: LibraryRepository,
        review_repository: ReviewRepository,
        google_books_service: GoogleBooksService,
    ) -> None:
        self.library_repository = library_repository
        self.review_repository = review_repository
        self.google_books_service = google_books_service

    async def get_recommendations(self, user_id: int, limit: int = 8) -> list[GoogleBookSearchResult]:
        reviews = await self.review_repository.list_for_user(user_id)
        library_items = await self.library_repository.list_for_user(user_id)

        seed_terms: list[str] = []
        for review in reviews:
            if review.rating >= 4:
                if review.book.authors:
                    seed_terms.extend(review.book.authors.split(", "))
                seed_terms.extend(word for word in review.book.title.split() if len(word) > 3)

        if not seed_terms:
            for item in library_items[:4]:
                seed_terms.extend(word for word in item.book.title.split() if len(word) > 3)

        if not seed_terms:
            return []

        most_common_terms = [term for term, _ in Counter(seed_terms).most_common(3)]
        query = " ".join(most_common_terms)
        recommendations = await self.google_books_service.search_books(
            query,
            max_results=limit * 2,
            library_repository=self.library_repository,
            user_id=user_id,
        )
        return [book for book in recommendations if not book.already_in_library][:limit]
