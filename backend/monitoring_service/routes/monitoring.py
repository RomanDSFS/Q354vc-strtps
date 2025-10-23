from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_reports():
    return {"message": "List of reports"}

@router.post("/")
async def create_report():
    return {"message": "Report created"}
