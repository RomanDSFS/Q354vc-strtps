from fastapi import APIRouter, HTTPException, Depends
import httpx
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

router = APIRouter()

AUTH_SERVICE_URL = "http://127.0.0.1:8001"  # URL микросервиса авторизации
#oauth2_scheme = OAuth2PasswordBearer(tokenUrl="http://127.0.0.1:8001/auth/login")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ✅ Модели запросов
#class LoginRequest(BaseModel):
   # username: str
   # password: str

class RegisterRequest(BaseModel):
    email: str
    company_name: str
    contacts: str
    password: str
    full_name: str
    role: str

class RefreshRequest(BaseModel):
    refresh_token: str

class UpdateProfileRequest(BaseModel):
    full_name: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# ✅ 1. Регистрация пользователя
@router.post("/register", summary="Регистрация пользователя")
async def register(request: RegisterRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/auth/register", json=request.dict())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()

# ✅ 2. Логин
"""
@router.post("/login", summary="Аутентификация пользователя")
async def login(request: LoginRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/login", data=request.dict())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()"""

@router.post("/login", summary="Аутентификация пользователя")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/auth/login", data=form_data.__dict__) #data=form_data)#.dict())  # ✅ Теперь точно form-data
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()

# ✅ 3. Обновление Access-токена
@router.post("/refresh", summary="Обновление Access-токена")
async def refresh_token(request: RefreshRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/auth/refresh", json=request.dict())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()

# ✅ 4. Выход из системы
@router.post("/logout", summary="Выход из системы")
async def logout(request: RefreshRequest):
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/auth/logout", json=request.dict())
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()

# ✅ 5. Получение профиля пользователя
@router.get("/me", summary="Получение информации о текущем пользователе")
async def get_user_profile(token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{AUTH_SERVICE_URL}/auth/me", headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()

# ✅ 6. Обновление профиля пользователя
@router.put("/update-profile", summary="Обновление профиля пользователя")
async def update_profile(request: UpdateProfileRequest, token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.put(f"{AUTH_SERVICE_URL}/auth/update-profile", json=request.dict(), headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()

# ✅ 7. Смена пароля пользователя
@router.post("/change-password", summary="Смена пароля пользователя")
async def change_password(request: ChangePasswordRequest, token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AUTH_SERVICE_URL}/auth/change-password", json=request.dict(), headers=headers)
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        return response.json()
