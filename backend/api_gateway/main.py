from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from api_gateway.routes import auth, sourcing, investors, kpi, decisions, deals, monitoring, exit
#from routes import sourcing

app = FastAPI(
    title="APP_5 API",
    description="API для венчурных инвесторов и стартапов",
    version="1.0.0",
    openapi_url="/openapi.json"
)

app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
#app.include_router(sourcing.router, prefix="/sourcing")
app.include_router(sourcing.router, prefix="/startups", tags=["Startups"])
app.include_router(investors.router, prefix="/investors", tags=["Investors"])
app.include_router(deals.router, prefix="/deals", tags=["Deals"])
app.include_router(kpi.router, prefix="/kpi", tags=["KPI Metrics"])
app.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
app.include_router(decisions.router, prefix="/decisions", tags=["Decisions"])
app.include_router(exit.router, prefix="/exit", tags=["Exit"])

def custom_openapi():
    del app.openapi_schema
    app.openapi_schema = get_openapi(
        title="APP_5 API",
        version="1.0.0",
        description="API для автоматизации принятия решений венчурными инвесторами",
        routes=app.routes,
    )
    return app.openapi_schema

app.openapi = custom_openapi


