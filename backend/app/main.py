from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

from app.routes.api_v1.api import api_router
from app.core.config import settings
from app.db import models, session

app = FastAPI(title="Personal Library API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_allow_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=settings.api_v1_str)


@app.on_event("startup")
async def startup_event() -> None:
    async_engine: AsyncEngine = session.engine
    async with async_engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)
        await conn.execute(text("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS category VARCHAR(64) NOT NULL DEFAULT 'General'"))
        await conn.execute(text("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS reading_status VARCHAR(32) NOT NULL DEFAULT 'to_read'"))
        await conn.execute(text("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS priority VARCHAR(32) NOT NULL DEFAULT 'medium'"))
        await conn.execute(text("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS source VARCHAR(64) NOT NULL DEFAULT 'manual'"))
        await conn.execute(text("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS reading_format VARCHAR(32) NOT NULL DEFAULT 'paper'"))
        await conn.execute(text("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS pages_total INTEGER"))
        await conn.execute(text("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS pages_read INTEGER"))
        await conn.execute(text("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS started_at DATE"))
        await conn.execute(text("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS finished_at DATE"))
        await conn.execute(text("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS last_opened_at DATE"))
        await conn.execute(text("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS personal_notes TEXT"))
        await conn.execute(text("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS favorite BOOLEAN NOT NULL DEFAULT FALSE"))
        await conn.execute(text("ALTER TABLE library_items ADD COLUMN IF NOT EXISTS tags TEXT"))
        await conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS reading_goal INTEGER NOT NULL DEFAULT 24"))


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Personal Library API is ready"}
