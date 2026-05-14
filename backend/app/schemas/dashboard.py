from pydantic import BaseModel


class DashboardMetric(BaseModel):
    # Generic label/value pair keeps chart-like dashboard sections uniform.
    label: str
    value: int


class DashboardOverview(BaseModel):
    # Single payload for the dashboard screen so it can render from one API call.
    books_in_library: int
    books_read_this_year: int
    books_in_progress: int
    books_to_read: int
    books_dnf: int
    favorite_books: int
    completion_rate: int
    average_rating: float
    reading_goal: int
    reading_goal_progress: int
    categories: list[DashboardMetric]
    formats: list[DashboardMetric]
    statuses: list[DashboardMetric]
    priorities: list[DashboardMetric]
    top_tags: list[DashboardMetric]


class DashboardGoalUpdate(BaseModel):
    # Kept as a DTO to leave room for future goal validation/versioning.
    reading_goal: int
