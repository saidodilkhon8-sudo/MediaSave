from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from pathlib import Path
from mediasave.app.config import settings


class Base(DeclarativeBase):
    pass


_engine = None
_async_session_factory = None


def get_engine():
    global _engine
    if _engine is None:
        db_url = settings.database_url
        if db_url.startswith("sqlite"):
            db_path = Path(db_url.replace("sqlite+aiosqlite:///", "").replace("sqlite:///", ""))
            if not db_path.is_absolute():
                db_path = Path.cwd() / db_path
            db_path.parent.mkdir(parents=True, exist_ok=True)
        _engine = create_async_engine(db_url, echo=False, future=True)
    return _engine


def get_session_factory():
    global _async_session_factory
    if _async_session_factory is None:
        _async_session_factory = async_sessionmaker(get_engine(), class_=AsyncSession, expire_on_commit=False)
    return _async_session_factory


@asynccontextmanager
async def get_session() -> AsyncSession:
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    from mediasave.app.database.models import Base as ModelsBase
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(ModelsBase.metadata.create_all)


async def close_db():
    global _engine, _async_session_factory
    if _engine:
        await _engine.dispose()
        _engine = None
        _async_session_factory = None
