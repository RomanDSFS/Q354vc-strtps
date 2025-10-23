from fastapi import APIRouter, HTTPException
import httpx
from pydantic import BaseModel
from typing import List, Dict

router = APIRouter()

DUE_DILIGENCE_SERVICE_URL = "http://127.0.0.1:8005/kpi"

# ✅ Модель запроса
class KPIRequest(BaseModel):
    """Запрос на анализ KPI стартапа"""
    startup_id: int
    stage: str  # Стадия стартапа
    type_deal: str  # Тип сделки
    selected_kpis: List[str]  # Выбранные метрики

# ✅ Модель ответа
class KPIResponse(BaseModel):
    """Ответ API с KPI и документами"""
    startup_id: int
    kpi_results: Dict[str, Dict]  # {"Сектор KPI": {"Название KPI": {"значение": "10%", "статус": "Получен/Нет"}}}
    recommended_docs: List[str]  # Документы по сделке

async def forward_request(endpoint: str, request: KPIRequest):
    """
    🔁 Проксирование запроса в due_diligence_service
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(f"{DUE_DILIGENCE_SERVICE_URL}{endpoint}", json=request.dict(), timeout=5.0)
            response.raise_for_status()
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Due Diligence Service is unavailable. Please try again later.")
        except httpx.ReadTimeout:
            raise HTTPException(status_code=504, detail="Due Diligence Service timeout. Please try again later.")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Error from due_diligence_service: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

    return response.json()

@router.post(
    "/analyze",
    summary="Анализ KPI стартапа",
    description="Проксирует запрос на анализ KPI стартапа в due_diligence_service",
    response_model=KPIResponse,
    responses={
        200: {
            "description": "Успешный анализ KPI",
            "content": {
                "application/json": {
                    "example": {
                        "startup_id": 101,
                        "kpi_results": {
                            "Financial Performance": {
                                "Revenue Growth": {"value": "10%", "status": "Получен"},
                                "Burn Rate": {"value": "Low", "status": "Нет"}
                            }
                        },
                        "recommended_docs": ["Term Sheet", "Investment Agreement"]
                    }
                }
            }
        },
        400: {
            "description": "Ошибка валидации (неверные параметры)",
            "content": {"application/json": {"example": {"detail": "Invalid startup_id"}}}
        },
        503: {
            "description": "Сервис временно недоступен",
            "content": {"application/json": {"example": {"detail": "Due Diligence Service is unavailable"}}}
        }
    }
)
async def analyze_kpi(request: KPIRequest):
    """
    🔁 Проксируем анализ KPI в due_diligence_service.
    """
    return await forward_request("/analyze", request)

# ✅ Проксируем отправку стартапа в Due Diligence
@router.post("/receive/{startup_id}", summary="Приём стартапа в Due Diligence")
async def receive_startup_for_due_diligence(startup_id: str, request: dict):
    """
    🔁 Проксирует отправку данных о стартапе в due_diligence_service.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{DUE_DILIGENCE_SERVICE_URL}/analyze/{startup_id}", json=request)
        return response.json()
