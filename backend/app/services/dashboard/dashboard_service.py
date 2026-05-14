from __future__ import annotations

from collections import Counter

from app.db.models import User
from app.repositories.auth.user_repository import UserRepository
from app.repositories.library.library_repository import LibraryRepository
from app.repositories.reviews.review_repository import ReviewRepository
from app.schemas.dashboard import DashboardGoalUpdate, DashboardMetric, DashboardOverview


class DashboardService:
    def __init__(
        self,
        library_repository: LibraryRepository,
        review_repository: ReviewRepository,
        user_repository: UserRepository,
    ) -> None:
        self.library_repository = library_repository
        self.review_repository = review_repository
        self.user_repository = user_repository

    async def get_overview(self, user: User) -> DashboardOverview:
        user_id = user.id
        library_items = await self.library_repository.list_for_user(user_id)
        reviews = await self.review_repository.list_for_user(user_id)
        # Compute dashboard values from persisted library state only, making the
        # endpoint deterministic and easy to verify in CI.
        books_in_progress = sum(1 for item in library_items if item.reading_status == "reading")
        books_to_read = sum(1 for item in library_items if item.reading_status == "to_read")
        books_dnf = sum(1 for item in library_items if item.reading_status == "dnf")
        finished_books = sum(1 for item in library_items if item.reading_status == "finished")
        favorite_books = sum(1 for item in library_items if item.favorite)
        completion_rate = round((finished_books / len(library_items)) * 100) if library_items else 0
        average_rating = round(sum(review.rating for review in reviews) / len(reviews), 1) if reviews else 0.0
        reading_goal_progress = round((finished_books / user.reading_goal) * 100) if user.reading_goal else 0

        def to_metrics(counter: Counter[str]) -> list[DashboardMetric]:
            return [DashboardMetric(label=label, value=value) for label, value in counter.most_common()]

        categories = to_metrics(Counter(item.category for item in library_items))
        formats = to_metrics(Counter(item.reading_format for item in library_items))
        statuses = to_metrics(Counter(item.reading_status for item in library_items))
        priorities = to_metrics(Counter(item.priority for item in library_items))
        top_tags = to_metrics(
            Counter(
                # Tags are stored as a compact comma-separated field; normalize
                # whitespace here before turning them into metrics.
                tag.strip()
                for item in library_items
                for tag in (item.tags or "").split(",")
                if tag.strip()
            )
        )

        return DashboardOverview(
            books_in_library=len(library_items),
            books_read_this_year=finished_books,
            books_in_progress=books_in_progress,
            books_to_read=books_to_read,
            books_dnf=books_dnf,
            favorite_books=favorite_books,
            completion_rate=completion_rate,
            average_rating=average_rating,
            reading_goal=user.reading_goal,
            reading_goal_progress=reading_goal_progress,
            categories=categories,
            formats=formats,
            statuses=statuses,
            priorities=priorities,
            top_tags=top_tags,
        )

    async def update_goal(self, user: User, goal_in: DashboardGoalUpdate) -> DashboardOverview:
        await self.user_repository.update_reading_goal(user, goal_in.reading_goal)
        return await self.get_overview(user)
