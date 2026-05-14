from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(str(settings.database_url), future=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    # Keep attributes available after commits because route handlers often return
    # ORM objects that Pydantic serializes after the repository has committed.
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    # FastAPI owns one database session per request and closes it deterministically.
    async with AsyncSessionLocal() as session:
        yield session
