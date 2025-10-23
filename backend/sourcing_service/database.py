from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:cdcefdsqweS2Q@localhost:5432/venture_app")

# ✅ Асинхронный движок SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# ✅ Создаём асинхронную фабрику сессий
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# ✅ Асинхронный метод для получения сессии БД
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
