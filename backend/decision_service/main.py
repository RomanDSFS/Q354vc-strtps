from fastapi import FastAPI
from routes.decisions import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Decision Service")

# Добавляем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно ограничить конкретными доменами
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем маршруты API
app.include_router(router, prefix="/decisions", tags=["Decisions"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004, reload=True)
