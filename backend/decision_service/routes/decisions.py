from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

# ✅ Модель запроса
class DecisionRequest(BaseModel):
    startup_id: int
    decision: str  # "approve", "reject", "feedback"
    feedback: str | None = None  # Опциональный фидбек

@router.post("/choose", summary="Approve a Startup")
async def approve_startup(request: DecisionRequest):
    """
    Инвестор одобряет стартап.
    """
    return {"message": "Startup approved", "startup_id": request.startup_id}

@router.post("/reject", summary="Reject a Startup")
async def reject_startup(request: DecisionRequest):
    """
    Инвестор отклоняет стартап.
    """
    return {"message": "Startup rejected", "startup_id": request.startup_id}

@router.post("/feedback", summary="Provide Feedback to a Startup")
async def provide_feedback(request: DecisionRequest):
    """
    Инвестор оставляет фидбек стартапу.
    """
    return {"message": "Feedback sent", "startup_id": request.startup_id, "feedback": request.feedback}
