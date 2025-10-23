from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from auth_service.models import User, RefreshToken
from auth_service.database import get_db
from passlib.context import CryptContext
import jwt
import datetime
import os
import uuid
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import delete
from shared.schemas import CurrentUser

router = APIRouter()

# 🔹 Конфигурация токенов и шифрования паролей
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
REFRESH_SECRET_KEY = os.getenv("REFRESH_SECRET_KEY", "your_refresh_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180
REFRESH_TOKEN_EXPIRE_DAYS = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8001/auth/login")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ✅ 1. Асинхронная зависимость для БД
async def get_db_session():
    async for session in get_db():
        yield session

# ✅ 2. Регистрация и аутентификация

# 🔹 Модель запроса на регистрацию
class RegisterRequest(BaseModel):
    email: str
    company_name : str  
    contacts: str
    password: str  
    full_name: str
    role: str  # investor, founder, admin

# 🔹 Регистрация пользователя
@router.post("/register", summary="Регистрация пользователя")
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(User).where(User.email == request.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email уже зарегистрирован")

    if request.role not in ["investor", "founder", "admin"]:
        raise HTTPException(status_code=400, detail="Некорректная роль")

    hashed_password = pwd_context.hash(request.password)

    new_user = User(
        id=uuid.uuid4(),
        email=request.email,
        company_name=request.company_name, 
        contacts=request.contacts,
        password_hash=hashed_password,
        full_name=request.full_name,
        role=request.role
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"message": "Пользователь зарегистрирован"}

# 🔹 Модель ответа с токенами
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

# 🔹 Логин пользователя
@router.post("/login", response_model=TokenResponse, summary="Аутентификация пользователя")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()

    if not user or not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Неверные учетные данные")

    access_token = create_access_token({"sub": str(user.id), "role": user.role})
    refresh_token = create_refresh_token({"sub": str(user.id)})

    new_refresh = RefreshToken(id=uuid.uuid4(), user_id=user.id, token=refresh_token)
    db.add(new_refresh)
    await db.commit()

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "Bearer"}

# ✅ 3. Работа с токенами

# 🔹 Функция генерации Access Token
def create_access_token(data: dict):
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

# 🔹 Функция генерации Refresh Token
def create_refresh_token(data: dict):
    expire = datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    #expire = datetime.datetime.utcnow() + datetime.timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    data.update({"exp": expire})
    return jwt.encode(data, REFRESH_SECRET_KEY, algorithm=ALGORITHM)

# 🔹 Обновление Access-токена
class RefreshRequest(BaseModel):
    refresh_token: str

@router.post("/refresh", response_model=TokenResponse, summary="Обновление access-токена")
async def refresh_token(request: RefreshRequest, db: AsyncSession = Depends(get_db_session)):
    result = await db.execute(select(RefreshToken).where(RefreshToken.token == request.refresh_token))
    refresh_entry = result.scalars().first()

    if not refresh_entry:
        raise HTTPException(status_code=401, detail="Неверный refresh-токен")

    try:
        payload = jwt.decode(request.refresh_token, REFRESH_SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=401, detail="Пользователь не найден")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Refresh-токен истёк")

    new_access_token = create_access_token({"sub": str(user.id), "role": user.role})

    return {"access_token": new_access_token, "refresh_token": request.refresh_token, "token_type": "Bearer"}

# 🔹 Выход из системы (удаление Refresh-токена)
@router.post("/logout", summary="Выход из системы")
async def logout(request: RefreshRequest, db: AsyncSession = Depends(get_db_session)):
    await db.execute(delete(RefreshToken).where(RefreshToken.token == request.refresh_token))
    #await db.execute(select(RefreshToken).where(RefreshToken.token == request.refresh_token).delete())
    await db.commit()
    return {"message": "Вы вышли из системы"}

# ✅ 4. Авторизация и проверка прав доступа

# 🔹 Декодирование и проверка JWT токена
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db_session)) -> CurrentUser:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return CurrentUser(user_id=user.id, role=user.role)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

"""
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db_session)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
"""
# ✅ 5. Управление профилем пользователя

# 🔹 Получение информации о текущем пользователе
@router.get("/me", summary="Получение информации о текущем пользователе")
async def get_user_profile(current_user: CurrentUser  = Depends(get_current_user)):
    return current_user.model_dump()
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "company_name": current_user.company_name,
        "contacts": current_user.contacts,
        "role": current_user.role,
        "created_at": current_user.created_at,
        "updated_at": current_user.updated_at,
    }"""

# 🔹 Обновление профиля пользователя
class UpdateProfileRequest(BaseModel):
    full_name: str

@router.put("/update-profile", summary="Обновление профиля пользователя")
async def update_profile(request: UpdateProfileRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db_session)):
    current_user.full_name = request.full_name
    await db.commit()
    await db.refresh(current_user)
    return {"message": "Профиль обновлён"}

# 🔹 Смена пароля пользователя
class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

@router.post("/change-password", summary="Смена пароля пользователя")
async def change_password(request: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db_session)):
    if not pwd_context.verify(request.old_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Старый пароль неверен")

    current_user.password_hash = pwd_context.hash(request.new_password)
    await db.commit()
    return {"message": "Пароль успешно изменён"}

class TokenRequest(BaseModel):
    token: str

@router.post("/verify-token", summary="Верификация токена")
async def verify_token(request: TokenRequest):  #(token: str):
    try:
        payload = jwt.decode(request.token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        role = payload.get("role")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        return {"user_id": user_id, "role": role}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
