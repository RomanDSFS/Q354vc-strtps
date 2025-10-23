from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_reports():
    return {"message": "Отчеты по стартапам"}

@router.post("/")
async def create_report():
    return {"message": "Создание отчета"}
