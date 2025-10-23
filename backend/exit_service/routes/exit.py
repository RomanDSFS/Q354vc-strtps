from fastapi import APIRouter

router = APIRouter()

@router.post("/request")
async def request_exit(data: dict):
    return {"message": "Запрос на выход из сделки принят."}

@router.get("/calculate")
async def calculate_roi():
    return {"roi": "10% годовых"}
