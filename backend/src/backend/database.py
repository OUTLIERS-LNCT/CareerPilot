import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

# Load environment variables from .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the environment variables.")

# Create the asynchronous SQLAlchemy engine
engine = create_async_engine(DATABASE_URL, echo=True)

# Create a session maker for database operations
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy database models."""

    pass


async def get_async_session() -> AsyncSession:
    """Dependency to get a database session for FastAPI endpoints."""
    async with async_session_maker() as session:
        yield session