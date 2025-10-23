from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sourcing_service.database import get_db  # проверь путь!
from sourcing_service.models import User
from pydantic import BaseModel
from typing import List
import httpx

router = APIRouter()

class InvestorProfileResponse(BaseModel):
    investor_type: List[str]
    investment_stage: List[str]
    industry: List[str]
    region: List[str]
    min_check: float

@router.get("/profile/{investor_id}", response_model=InvestorProfileResponse, tags=["Investors"])
async def get_investor_profile(investor_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.id == investor_id, User.role == "investor"))
    investor = result.scalars().first()

    if not investor:
        raise HTTPException(status_code=404, detail="Investor not found")

    if not investor.investor_type or not investor.industry or not investor.investment_stage or not investor.region or investor.min_check is None:
        raise HTTPException(status_code=400, detail="Incomplete investor profile")

    return InvestorProfileResponse(
        investor_type=investor.investor_type,
        investment_stage=investor.investment_stage,
        industry=investor.industry,
        region=investor.region,
        min_check=investor.min_check
    )
