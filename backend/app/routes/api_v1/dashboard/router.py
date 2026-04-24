from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.db.session import get_db
from app.repositories.auth.user_repository import UserRepository
from app.repositories.library.library_repository import LibraryRepository
from app.repositories.reviews.review_repository import ReviewRepository
from app.routes.api_v1.dependencies import get_current_active_user
from app.schemas.dashboard import DashboardGoalUpdate, DashboardOverview
from app.services.dashboard.dashboard_service import DashboardService

router = APIRouter()


@router.get("/", response_model=DashboardOverview)
async def get_dashboard(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    service = DashboardService(LibraryRepository(db), ReviewRepository(db), UserRepository(db))
    return await service.get_overview(current_user)


@router.patch("/goal", response_model=DashboardOverview)
async def update_reading_goal(
    goal_in: DashboardGoalUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    service = DashboardService(LibraryRepository(db), ReviewRepository(db), UserRepository(db))
    return await service.update_goal(current_user, goal_in)
