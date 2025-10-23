from fastapi import FastAPI
from sourcing_service.routes import startups, investors

app = FastAPI(title="Sourcing Service")

app.include_router(startups.router, prefix="/startups", tags=["Startups"])
app.include_router(investors.router, prefix="/investors", tags=["Investors"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("sourcing_service.main:app", host="0.0.0.0", port=8002, reload=True)
