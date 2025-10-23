from fastapi import FastAPI
from routes import monitoring

app = FastAPI(title="Monitoring Service")

app.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8007, reload=True)
