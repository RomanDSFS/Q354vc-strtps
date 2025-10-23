from fastapi import APIRouter, HTTPException
import httpx
from pydantic import BaseModel

router = APIRouter()

DEAL_ROOM_SERVICE_URL = "http://127.0.0.1:8003/deals"

class DealRoomRequest(BaseModel):
    startup_id: int
    investor_id: int
    deal_terms: str

@router.post("/create", summary="Create a Deal Room", response_model=dict)
async def create_deal_room(request: DealRoomRequest):  
    """
    Проксирует создание сделки в deal_room_service.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{DEAL_ROOM_SERVICE_URL}/create", json=request.dict(), timeout=5.0)
            response.raise_for_status()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Deal Room Service is unavailable. Please try again later.")
        except httpx.ReadTimeout:
            raise HTTPException(status_code=504, detail="Deal Room Service timeout. Please try again later.")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error from deal_room_service: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return response.json()

@router.get("/{deal_id}", summary="Get Deal Room Info")
async def get_deal_room(deal_id: int):
    """
    Проксирует получение информации о сделке в deal_room_service.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{DEAL_ROOM_SERVICE_URL}/{deal_id}", timeout=5.0)
            response.raise_for_status()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Deal Room Service is unavailable. Please try again later.")
        except httpx.ReadTimeout:
            raise HTTPException(status_code=504, detail="Deal Room Service timeout. Please try again later.")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error from deal_room_service: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return response.json()
