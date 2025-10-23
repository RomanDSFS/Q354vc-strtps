from fastapi import FastAPI
from routes.kpi import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Due Diligence Service",
    description="API для анализа стартапов перед инвестицией",
    version="1.0.0"
)

# ✅ Добавляем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Подключаем маршруты API
app.include_router(router, prefix="/kpi", tags=["KPI Analysis"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005, reload=True)
