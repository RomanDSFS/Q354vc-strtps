
import sys
import os

# ✅ Добавляем `backend` и `auth_service` в PYTHONPATH, чтобы pytest находил модули
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../auth_service")))


import asyncio
import pytest
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm

# ✅ Теперь импортируются правильно
from database import Base
from database import get_db  # Исправленный импорт
from models import User, RefreshToken
from routes.auth import register, login, create_refresh_token, logout, refresh_token as refresh_token_endpoint
from routes.auth import RefreshRequest  # Импорт модели запроса

# ✅ Подключаем тестовую БД
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:cdcefdsqweS2Q@localhost:5432/venture_app_test"
engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=True)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# ✅ Контекст хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@pytest.fixture(scope="function")
async def db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # ✅ Создаём таблицы перед тестами

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

# ✅ Тест регистрации пользователя
@pytest.mark.asyncio
async def test_register_user(db: AsyncSession):
    request_data = {
        "email": "newuser@example.com",
        "password": "NewPassword123",
        "full_name": "New User",
        "role": "investor"
    }
    
    # ✅ ВАЖНО: register ожидает объект `RegisterRequest`, а не `dict`
    from routes.auth import RegisterRequest  # Импорт модели запроса
    request_obj = RegisterRequest(**request_data)  # Создаём Pydantic-объект
    
    response = await register(request=request_obj, db=db)  # ✅ Передаём объект в `register`
    assert response["message"] == "Пользователь зарегистрирован"
    
    result = await db.execute(select(User).where(User.email == request_data["email"]))
    user = result.scalars().first()
    
    assert user is not None
    assert user.full_name == "New User"
    assert user.role == "investor"
    assert pwd_context.verify("NewPassword123", user.password_hash)  # ✅ Проверяем, что пароль захеширован

# ✅ Тест логина пользователя
@pytest.mark.asyncio
async def test_login_user(db: AsyncSession):
    user = User(
        id=str(uuid.uuid4()),
        email="loginuser@example.com",
        password_hash=pwd_context.hash("TestPassword"),  # ✅ Хешируем пароль перед сохранением
        full_name="Login User",
        role="investor"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # ✅ Используем `OAuth2PasswordRequestForm`, но в тестах он принимает `dict`
    form_data = OAuth2PasswordRequestForm(
        username="loginuser@example.com",
        password="TestPassword"
    )

    response = await login(form_data, db)

    assert "access_token" in response
    assert "refresh_token" in response
    assert response["token_type"] == "Bearer"
    assert response["access_token"] is not None
    assert response["refresh_token"] is not None


# ✅ Тест обновления access-токена
@pytest.mark.asyncio
async def test_refresh_token(db: AsyncSession):
    """Тест проверяет обновление access-токена по refresh-токену"""

    # 🔹 Создаем тестового пользователя
    user = User(
        id=str(uuid.uuid4()),
        email="refreshuser@example.com",
        password_hash=pwd_context.hash("SecurePassword123"),
        full_name="Refresh User",
        role="investor"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 🔹 Генерируем refresh-токен и сохраняем его в БД
    from routes.auth import create_refresh_token
    refresh_token = create_refresh_token({"sub": str(user.id)})

    new_refresh_token = RefreshToken(id=uuid.uuid4(), user_id=user.id, token=refresh_token)
    db.add(new_refresh_token)
    await db.commit()

    # ✅ Создаем Pydantic-объект вместо dict
    request_obj = RefreshRequest(refresh_token=refresh_token)

    # 🔹 Отправляем запрос на обновление access-токена
    from routes.auth import refresh_token as refresh_token_endpoint
    response = await refresh_token_endpoint(request_obj, db)

    # 🔹 Проверяем, что новый токен сгенерирован
    assert "access_token" in response
    assert response["access_token"] is not None
    assert response["token_type"] == "Bearer"
    assert response["refresh_token"] == refresh_token  # refresh-токен остается тем же

# ✅ Тест выхода из системы
@pytest.mark.asyncio
async def test_logout(db: AsyncSession):
    """Тест проверяет выход пользователя из системы (удаление refresh-токена)"""

    # 🔹 Создаем тестового пользователя
    user = User(
        id=str(uuid.uuid4()),
        email="logoutuser@example.com",
        password_hash=pwd_context.hash("LogoutTestPassword"),
        full_name="Logout User",
        role="investor"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 🔹 Генерируем refresh-токен и сохраняем его в БД
    from routes.auth import create_refresh_token
    refresh_token = create_refresh_token({"sub": str(user.id)})

    logout_refresh = RefreshToken(id=uuid.uuid4(), user_id=user.id, token=refresh_token)
    db.add(logout_refresh)
    await db.commit()

    # ✅ Создаем Pydantic-объект вместо dict
    request_obj = RefreshRequest(refresh_token=refresh_token)

    # 🔹 Отправляем запрос на `/logout`
    from routes.auth import logout
    response = await logout(request_obj, db)

    # 🔹 Проверяем успешный выход
    assert response["message"] == "Вы вышли из системы"

    # 🔹 Проверяем, что refresh-токен удален из БД
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
    assert result.scalars().first() is None  # Токен должен быть удален

# ✅ Тест получения информации о текущем пользователе
@pytest.mark.asyncio
async def test_get_user_profile(db: AsyncSession):
    """Тест проверяет получение данных текущего пользователя"""

    # 🔹 Создаем тестового пользователя
    user = User(
        id=str(uuid.uuid4()),
        email="profileuser@example.com",
        password_hash=pwd_context.hash("ProfilePassword"),
        full_name="Profile User",
        role="investor"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 🔹 Генерируем access-токен
    from routes.auth import create_access_token
    access_token = create_access_token({"sub": str(user.id), "role": user.role})

    # 🔹 Отправляем запрос на `/me`
    from routes.auth import get_user_profile
    response = await get_user_profile(current_user=user)

    # 🔹 Проверяем, что полученные данные соответствуют пользователю
    assert response["id"] == str(user.id)
    assert response["email"] == user.email
    assert response["full_name"] == user.full_name
    assert response["role"] == user.role

# ✅ Тест обновления профиля пользователя
@pytest.mark.asyncio
async def test_update_profile(db: AsyncSession):
    """Тест проверяет обновление профиля пользователя"""

    # 🔹 Создаем тестового пользователя
    user = User(
        id=str(uuid.uuid4()),
        email="updateprofile@example.com",
        password_hash=pwd_context.hash("UpdateProfilePassword"),
        full_name="Old Name",
        role="investor"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 🔹 Создаем Pydantic-объект запроса
    from routes.auth import UpdateProfileRequest, update_profile
    request_obj = UpdateProfileRequest(full_name="New Name")

    # 🔹 Отправляем запрос на обновление профиля
    response = await update_profile(request_obj, current_user=user, db=db)

    # 🔹 Проверяем успешный ответ
    assert response["message"] == "Профиль обновлён"

    # 🔹 Проверяем, что имя обновилось в БД
    await db.refresh(user)
    assert user.full_name == "New Name"

# ✅ Тест смены пароля пользователя
@pytest.mark.asyncio
async def test_change_password(db: AsyncSession):
    """Тест проверяет смену пароля пользователя"""

    # 🔹 Создаем тестового пользователя
    user = User(
        id=str(uuid.uuid4()),
        email="changepass@example.com",
        password_hash=pwd_context.hash("OldPassword123"),
        full_name="Password User",
        role="investor"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 🔹 Создаем Pydantic-объект запроса
    from routes.auth import ChangePasswordRequest, change_password
    request_obj = ChangePasswordRequest(old_password="OldPassword123", new_password="NewSecurePassword456")

    # 🔹 Отправляем запрос на смену пароля
    response = await change_password(request_obj, current_user=user, db=db)

    # 🔹 Проверяем успешный ответ
    assert response["message"] == "Пароль успешно изменён"

    # 🔹 Проверяем, что пароль изменился в БД
    await db.refresh(user)
    assert pwd_context.verify("NewSecurePassword456", user.password_hash)  # Новый пароль должен хешироваться

"""
# ✅ Тест обновления access-токена
@pytest.mark.asyncio
async def test_refresh_token(db: AsyncSession):
    #Тест проверяет обновление access-токена по refresh-токену
    
    # 🔹 Создаем тестового пользователя
    user = User(
        id=str(uuid.uuid4()),
        email="refreshuser@example.com",
        password_hash=pwd_context.hash("SecurePassword123"),
        full_name="Refresh User",
        role="investor"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 🔹 Генерируем refresh-токен и сохраняем его в БД
    #from routes.auth import create_refresh_token
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    new_refresh_token = RefreshToken(id=uuid.uuid4(), user_id=user.id, token=refresh_token)
    db.add(new_refresh_token)
    await db.commit()

    # 🔹 Отправляем запрос на обновление access-токена
    #from routes.auth import refresh_token as refresh_token_endpoint
    request_data = {"refresh_token": refresh_token}
    
    response = await refresh_token_endpoint(request_data, db)
    
    # 🔹 Проверяем, что новый токен сгенерирован
    assert "access_token" in response
    assert response["access_token"] is not None
    assert response["token_type"] == "Bearer"
    assert response["refresh_token"] == refresh_token  # refresh-токен остается тем же

# ✅ Тест выхода из системы
@pytest.mark.asyncio
async def test_logout(db: AsyncSession):
    #Тест проверяет выход пользователя из системы (удаление refresh-токена)
    
    # 🔹 Создаем тестового пользователя
    user = User(
        id=str(uuid.uuid4()),
        email="logoutuser@example.com",
        password_hash=pwd_context.hash("LogoutTestPassword"),
        full_name="Logout User",
        role="investor"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # 🔹 Генерируем refresh-токен и сохраняем его в БД
    #from routes.auth import create_refresh_token
    refresh_token = create_refresh_token({"sub": str(user.id)})
    
    logout_refresh = RefreshToken(id=uuid.uuid4(), user_id=user.id, token=refresh_token)
    db.add(logout_refresh)
    await db.commit()

    # 🔹 Отправляем запрос на `/logout`
    #from routes.auth import logout
    request_data = {"refresh_token": refresh_token}
    
    response = await logout(request_data, db)
    
    # 🔹 Проверяем успешный выход
    assert response["message"] == "Вы вышли из системы"

    # 🔹 Проверяем, что refresh-токен удален из БД
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == refresh_token))
    assert result.scalars().first() is None  # Токен должен быть удален"""
