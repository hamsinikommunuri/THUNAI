"""
THUNAI Database Connection & Session Management
Supports SQLite (async aiosqlite) for lightweight local deployment
and PostgreSQL (Supabase / Render Postgres) for production via DATABASE_URL.
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from backend.app.core.config import settings

# Engine configuration
database_url = settings.DATABASE_URL
if database_url.startswith("sqlite"):
    engine = create_async_engine(database_url, connect_args={"check_same_thread": False})
else:
    # Handle standard postgres:// to postgresql+asyncpg:// if provided
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    engine = create_async_engine(database_url, echo=False)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
