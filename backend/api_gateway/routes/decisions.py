from fastapi import APIRouter, HTTPException
import httpx
from pydantic import BaseModel

router = APIRouter()

DECISION_SERVICE_URL = "http://127.0.0.1:8004/decisions"

# ✅ Описание модели запроса
class DecisionRequest(BaseModel):
    startup_id: int
    decision: str
    feedback: str | None = None

async def forward_request(endpoint: str, request: DecisionRequest):
    """
    Функция для отправки запроса в decision_service с обработкой ошибок.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{DECISION_SERVICE_URL}{endpoint}", json=request.dict(), timeout=5.0)
            response.raise_for_status()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Decision Service is unavailable. Please try again later.")
        except httpx.ReadTimeout:
            raise HTTPException(status_code=504, detail="Decision Service timeout. Please try again later.")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error from decision_service: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return response.json()

@router.post("/choose", summary="Approve a Startup")
async def approve_startup(request: DecisionRequest):
    """
    Проксируем одобрение стартапа в decision_service.
    """
    return await forward_request("/choose", request)

@router.post("/reject", summary="Reject a Startup")
async def reject_startup(request: DecisionRequest):
    """
    Проксируем отклонение стартапа в decision_service.
    """
    return await forward_request("/reject", request)

@router.post("/feedback", summary="Provide Feedback to a Startup")
async def provide_feedback(request: DecisionRequest):
    """
    Проксируем фидбек стартапу в decision_service.
    """
    return await forward_request("/feedback", request)
