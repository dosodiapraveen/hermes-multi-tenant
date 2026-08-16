from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.config import settings

engine = create_async_engine(
    settings.db_url,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,  # Recycle connections every 30 minutes
)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.connect() as c:
        await c.execute(text("SELECT 1"))

async def close_db():
    await engine.dispose()

async def get_db():
    async with async_session_factory() as s:
        try:
            yield s
            await s.commit()
        except:
            await s.rollback()
            raise
