from fastapi import APIRouter

from app.routes.api_v1.dashboard.router import router as dashboard_router
from app.routes.api_v1.auth.router import router as auth_router
from app.routes.api_v1.books.router import router as books_router
from app.routes.api_v1.library.router import router as library_router
from app.routes.api_v1.recommendations.router import router as recommendations_router
from app.routes.api_v1.reviews.router import router as reviews_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(books_router, prefix="/books", tags=["books"])
api_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(library_router, prefix="/library", tags=["library"])
api_router.include_router(recommendations_router, prefix="/recommendations", tags=["recommendations"])
api_router.include_router(reviews_router, prefix="/reviews", tags=["reviews"])
