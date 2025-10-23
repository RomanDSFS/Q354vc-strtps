from fastapi import FastAPI
from auth_service.routes import auth
#from routes.auth import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Auth Service")

# ✅ Добавляем CORS, чтобы фронтенд мог отправлять запросы
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 👈 Указываем фронтенд
    allow_credentials=True,
    allow_methods=["*"],  # 👈 Разрешаем все методы (GET, POST, PUT, DELETE)
    allow_headers=["*"],  # 👈 Разрешаем все заголовки
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
