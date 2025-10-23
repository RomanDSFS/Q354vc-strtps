from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# ✅ Описание модели запроса (чтобы Swagger UI показывал параметры)
class DealRoomRequest(BaseModel):
    startup_id: int
    investor_id: int
    deal_terms: str

@router.post("/create", summary="Create a Deal Room")
async def create_deal_room(request: DealRoomRequest):  
    """
    Создаёт виртуальную комнату для сделки между стартапом и инвестором.
    """
    return {
        "message": "Deal room created successfully",
        "startup_id": request.startup_id,
        "investor_id": request.investor_id,
        "deal_terms": request.deal_terms
    }

@router.get("/{deal_id}", summary="Get Deal Room Info")
async def get_deal_room(deal_id: int):
    return {"deal_id": deal_id, "status": "Active"}
