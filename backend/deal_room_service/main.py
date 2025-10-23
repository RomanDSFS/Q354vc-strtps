from fastapi import FastAPI
from routes.deals import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Deal Room Service")

# Добавляем CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Можно ограничить только нужные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/deals", tags=["Deals"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003, reload=True)
