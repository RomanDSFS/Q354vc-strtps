import os
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# ✅ Используем асинхронный драйвер PostgreSQL (asyncpg)

# ✅ Создаём асинхронный движок SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# ✅ Создаём фабрику сессий для работы с БД
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,  # Используем асинхронные сессии!
    expire_on_commit=False
)

Base = declarative_base()

# ✅ Функция для получения асинхронной сессии БД
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session  # Возвращаем асинхронную сессию
