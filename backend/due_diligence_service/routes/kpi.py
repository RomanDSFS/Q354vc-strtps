from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict
from sqlalchemy.orm import Session
from database import get_db
from models import DueDiligenceStartup

router = APIRouter()

# ✅ Модель запроса на анализ KPI
class KPIRequest(BaseModel):
    startup_id: str
    company_name: str
    industry: str
    stage: str
    region: str
    min_check: float

# ✅ Модель ответа
class KPIResponse(BaseModel):
    startup_id: str
    kpi_results: Dict[str, Dict]
    recommended_docs: List[str]

# ✅ Приём данных от sourcing_service
@router.post("/analyze/{startup_id}", summary="Приём стартапа для Due Diligence")
async def receive_startup_for_due_diligence(startup_id: str, request: KPIRequest, db: Session = Depends(get_db)):
    """
    Получает данные о стартапе из `sourcing_service` и добавляет в Due Diligence.
    """
    existing_entry = db.query(DueDiligenceStartup).filter(DueDiligenceStartup.startup_id == startup_id).first()
    if existing_entry:
        raise HTTPException(status_code=400, detail="Стартап уже в Due Diligence")

    new_entry = DueDiligenceStartup(
        startup_id=request.startup_id,
        company_name=request.company_name,
        industry=request.industry,
        stage=request.stage,
        region=request.region,
        min_check=request.min_check
    )
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)

    return {"message": "Стартап успешно добавлен в Due Diligence"}

# ✅ Анализ KPI (уже был)
@router.post("/analyze", summary="Анализ KPI стартапа", response_model=KPIResponse)
async def analyze_kpi(request: KPIRequest):
    """
    Анализирует KPI стартапа и выдаёт список ключевых показателей и документов.
    """
    if not request.startup_id:
        raise HTTPException(status_code=400, detail="Invalid startup_id")

    # ✅ Фиктивные данные (заменим на БД)
    kpi_results = {
        "Financial Performance": {
            "Revenue Growth": {"value": "38%", "status": "Получен"},
            "Burn Rate": {"value": "Low", "status": "Нет"}
        }
    }
    recommended_docs = ["Term Sheet", "Investment Agreement"]

    return KPIResponse(
        startup_id=request.startup_id,
        kpi_results=kpi_results,
        recommended_docs=recommended_docs
    )
