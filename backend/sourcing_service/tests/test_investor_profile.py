import sys
import os

# ✅ Добавляем `backend` и `sourcing_service` в PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../sourcing_service")))

import asyncio
import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from fastapi import HTTPException
from database import Base
from database import get_db
from models import User, Startup
from routes.startups import save_investor_profile, save_founder_profile

# ✅ Подключаем тестовую БД
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:cdcefdsqweS2Q@localhost:5432/venture_app_test"
engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture(scope="function")
async def db():
    """Создание тестовой базы перед каждым тестом"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # ✅ Создаем таблицы перед тестами

    async with async_session_maker() as session:
        yield session  # ✅ Передаём сессию в тест

    async with engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):  # ✅ Очищаем данные, но не удаляем таблицы
            await conn.execute(table.delete())  
        await conn.commit()

    # ✅ ЯВНОЕ ЗАКРЫТИЕ СОЕДИНЕНИЯ
    await engine.dispose()

@pytest.fixture(scope="session", autouse=True)
def reset_event_loop():
    asyncio.set_event_loop(asyncio.new_event_loop())

# ✅ Тесты для инвестора
@pytest.mark.asyncio
async def test_update_investor_profile_success(db: AsyncSession):
    """✅ Тест успешного обновления профиля инвестора"""
    
    investor = User(
        id=str(uuid.uuid4()),
        email="investor@example.com",
        password_hash="hashedpassword",
        company_name = "Columnus", # - И УБРАТЬ ИЗ МОДЕЛС СОУРС_СЕКВИС
        contacts = "CString",#- И УБРАТЬ ИЗ МОДЕЛС СОУРС_СЕРВИС
        full_name="Investor Name",
        role="investor"
    )
    db.add(investor)
    await db.commit()
    await db.refresh(investor)

    investor_data = {
        "investor_type": ["VC", "Angel"],
        "investment_stage": ["Seed", "Series A"],
        "industry": ["Tech", "AI"],
        "region": ["USA", "Europe"],
        "min_check": 50000
    }

    response = await save_investor_profile(investor_data, db, {"id": investor.id, "role": "investor"})

    assert response["message"] == "Investor profile updated successfully"

    result = await db.execute(select(User).where(User.id == investor.id))
    updated_investor = result.scalars().first()

    assert updated_investor is not None
    assert updated_investor.investor_type == investor_data["investor_type"]
    assert updated_investor.investment_stage == investor_data["investment_stage"]
    assert updated_investor.industry == investor_data["industry"]
    assert updated_investor.region == investor_data["region"]
    assert updated_investor.min_check == investor_data["min_check"]

@pytest.mark.asyncio
async def test_update_investor_profile_wrong_role(db: AsyncSession):
    """❌ Тест ошибки при попытке обновления профиля не-инвестором"""
    
    founder = User(
        id=str(uuid.uuid4()),
        email="founder@example.com",
        password_hash="hashedpassword",
        company_name = "Columnus", # - И УБРАТЬ ИЗ МОДЕЛС СОУРС_СЕКВИС
        contacts = "CString",#- И УБРАТЬ ИЗ МОДЕЛС СОУРС_СЕРВИС
        full_name="Founder Name",
        role="founder"
    )
    db.add(founder)
    await db.commit()
    await db.refresh(founder)

    investor_data = {
        "investor_type": ["VC"],
        "investment_stage": ["Seed"],
        "industry": ["Tech"],
        "region": ["USA"],
        "min_check": 100000
    }

    with pytest.raises(HTTPException) as exc_info:
        await save_investor_profile(investor_data, db, {"id": founder.id, "role": "founder"})

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Access denied"

@pytest.mark.asyncio
async def test_update_founder_profile_success(db: AsyncSession):
    """✅ Успешное обновление профиля основателя"""

    # 🔹 Создаем пользователя (фаундера)
    founder = User(
        id=str(uuid.uuid4()),
        email="founder@example.com",
        password_hash="hashed_password",
        company_name = "Mozsau", # - И УБРАТЬ ИЗ МОДЕЛС СОУРС_СЕКВИС
        contacts = "Ddsrfffffff",
        full_name="Founder User",
        role="founder"
    )
    db.add(founder)
    await db.commit()
    await db.refresh(founder)

    # 🔹 Создаем стартап перед обновлением профиля
    startup = Startup(
        id=str(uuid.uuid4()),
        founder_id=founder.id,
        #company_name="Tech Startup",
        industry=["AI"],
        stage=["Pre-Seed"],
        region=["USA"],
        min_check=20000,
        #contacts="contact@startup.com"
    )
    db.add(startup)
    await db.commit()
    await db.refresh(startup)

    # 🔹 Данные для обновления профиля
    request_data = {
        "stage": ["Series A"],
        "industry": ["AI", "FinTech"],
        "region": ["USA", "Europe"],
        "min_check": 50000
    }

    # 🔹 Вызываем функцию обновления профиля
    response = await save_founder_profile(request_data, db, current_user={"id": founder.id, "role": "founder"})

    # 🔹 Проверяем успешное выполнение
    assert response["message"] == "Founder profile updated successfully"

    # 🔹 Проверяем обновленные данные в БД
    result = await db.execute(select(Startup).where(Startup.founder_id == founder.id))
    updated_startup = result.scalars().first()

    assert updated_startup is not None
    assert updated_startup.stage == ["Series A"]
    assert updated_startup.industry == ["AI", "FinTech"]
    assert updated_startup.region == ["USA", "Europe"]
    assert updated_startup.min_check == 50000

"""
# ✅ Тесты для основателя (фаундера)
@pytest.mark.asyncio
async def test_update_founder_profile_success(db: AsyncSession):
    #✅ Успешное обновление профиля основателя

    founder = User(
        id=str(uuid.uuid4()),
        email="founder@example.com",
        password_hash="hashed_password",
        company_name = "Mozsau", # - И УБРАТЬ ИЗ МОДЕЛС СОУРС_СЕКВИС
        contacts = "Ddsrfffffff",
        full_name="Founder User",
        role="founder"
    )
    db.add(founder)
    await db.commit()
    await db.refresh(founder)

    request_data = {
        "stage": ["Seed"],
        "industry": ["AI", "FinTech"],
        "region": ["USA", "Europe"],
        "min_check": 50000
    }

    response = await save_founder_profile(request_data, db, current_user={"id": founder.id, "role": "founder"})

    assert response["message"] == "Founder profile updated successfully"

    result = await db.execute(select(Startup).where(Startup.founder_id == founder.id))
    updated_startup = result.scalars().first()

    assert updated_startup is not None
    assert updated_startup.stage == ["Seed"]
    assert updated_startup.industry == ["AI", "FinTech"]
    assert updated_startup.region == ["USA", "Europe"]
    assert updated_startup.min_check == 50000
"""
@pytest.mark.asyncio
async def test_update_founder_profile_wrong_role(db: AsyncSession):
    #❌ Ошибка: Попытка обновить профиль не-фаундером

    investor = User(
        id=str(uuid.uuid4()),
        email="investor@example.com",
        password_hash="hashed_password",
        company_name = "Columnus", # - И УБРАТЬ ИЗ МОДЕЛС СОУРС_СЕКВИС
        contacts = "CString",
        full_name="Investor User",
        role="investor"
    )
    db.add(investor)
    await db.commit()
    await db.refresh(investor)

    request_data = {
        "stage": ["Series A"],
        "industry": ["HealthTech"],
        "region": ["Asia"],
        "min_check": 100000
    }

    with pytest.raises(HTTPException) as exc_info:
        await save_founder_profile(request_data, db, current_user={"id": investor.id, "role": "investor"})

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Access denied"
