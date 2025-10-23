from fastapi import FastAPI
from routes import exit

app = FastAPI(title="Exit Service")

app.include_router(exit.router, prefix="/exit", tags=["Exit"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006, reload=True)
