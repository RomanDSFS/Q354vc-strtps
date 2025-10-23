#import sys
#import os
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from sqlalchemy.sql import cast, exists, func
#from sqlalchemy.orm import joinedload
from sqlalchemy.dialects.postgresql import ARRAY, VARCHAR, TEXT
from sourcing_service.database import get_db
from sourcing_service.models import Startup, User, AnalysisResult, StartupScore
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Union
from auth_service.routes.auth import get_current_user
#import shutil
import logging
import uuid
import httpx
import traceback
from datetime import datetime
from sourcing_service.analysis import save_uploaded_file, analyze_startup_score_async
#import requests
#import json
from config import UPLOAD_DIR
from fastapi.security import OAuth2PasswordBearer
#from starlette.responses import JSONResponse
from uuid import UUID
from sourcing_service.schemas.startups import (
    StartupResponse, InvestorProfileUpdate, FounderProfileUpdate,
    StartupFilterRequest, Answer, StartupScoreDetails, FillTemplateRequest,
    StartupScoreBatchResponse,)
from shared.schemas import CurrentUser

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

router = APIRouter()
AUTH_SERVICE_VERIFY_URL = "http://127.0.0.1:8001/auth/verify-token"
DUE_DILIGENCE_SERVICE_URL = "http://127.0.0.1:8005/kpi/analyze"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# ✅ 1. Обновить профиль инвестора
@router.post("/investors/profile", summary="Обновить профиль инвестора", tags=["Startups"])
async def save_investor_profile(
    investor_data: InvestorProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    if current_user.role != "investor":
        raise HTTPException(status_code=403, detail="Access denied")

    stmt = (
        update(User)
        .where(User.id == current_user.user_id)
        .values(
            investor_type=investor_data.investor_type,
            investment_stage=investor_data.investment_stage,
            industry=investor_data.industry,
            region=investor_data.region,
            min_check=investor_data.min_check
        )
    )
    await db.execute(stmt)
    await db.commit()

    return {"message": "Investor profile updated successfully"}

# ✅ 2. Обновить профиль основателя
@router.post("/founders/profile", summary="Обновить профиль основателя", tags=["Startups"])
async def save_founder_profile(
    founder_data: FounderProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    logging.info(f"Полученный current_user: {current_user}")

    if not current_user.user_id:
        raise HTTPException(status_code=401, detail="Invalid token: No user ID found")

    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Access denied")

    stmt = (
        update(Startup)
        .where(Startup.founder_id == current_user.user_id)
        .values(
            name=founder_data.name,
            description=founder_data.description,
            stage=founder_data.stage,
            industry=founder_data.industry,
            region=founder_data.region,
            min_check=founder_data.min_check
        )
    )
    result = await db.execute(stmt)

    if result.rowcount == 0:
        new_startup = Startup(
            founder_id=current_user.user_id,
            name=founder_data.name,
            description=founder_data.description,
            stage=founder_data.stage,
            industry=founder_data.industry,
            region=founder_data.region,
            min_check=founder_data.min_check,
        )
        db.add(new_startup)

    await db.commit()
    return {"message": "Founder profile updated successfully"}

# ✅ 3. Загрузить Pitch Deck и провести анализ
@router.post("/founders/upload", summary="Загрузить Pitch Deck и провести анализ", response_model=dict, tags=["Startups"])
async def upload_pitch_deck(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    try:
        if current_user.role != "founder":
            raise HTTPException(status_code=403, detail="Access denied")

        file_path = await save_uploaded_file(file)
        file_ext = file.filename.split('.')[-1]

        startup_result = await db.execute(select(Startup).filter(Startup.founder_id == current_user.user_id))
        startup = startup_result.scalars().first()
        if not startup:
            raise HTTPException(status_code=404, detail="Стартап не найден")

        stmt = (
            update(Startup)
            .where(Startup.founder_id == current_user.user_id)
            .values(pitch_deck=file_path)
        )
        await db.execute(stmt)
        await db.commit()

        print("Starting analysis for:", file_path)

        allowed_extensions = {"pdf", "pptx"}
        if file_ext not in allowed_extensions:
            raise HTTPException(status_code=400, detail="Unsupported file format. Only PDF and PPTX are allowed.")

        result = await analyze_startup_score_async(file_path, file_ext)

        new_analysis = AnalysisResult(
            startup_id=startup.id,
            founder_id=current_user.user_id,
            file_path=file_path,
            startup_score=result["startup_score"],
            usp_score=result["details"].get("USP"),
            market_score=result["details"].get("Market"),
            business_model_score=result["details"].get("Business Model"),
            team_score=result["details"].get("Team"),
            finance_score=result["details"].get("Finance"),
            created_at=datetime.utcnow()
        )
        db.add(new_analysis)
        await db.commit()
        await db.refresh(new_analysis)

        return {
            "message": "Pitch deck uploaded and analyzed successfully",
            "file_path": file_path,
            "analysis_result": {
                "startup_score": result["startup_score"],
            }
        }

    except HTTPException as http_error:
        print(f"HTTP Exception: {http_error.detail}")
        raise http_error

    except Exception as e:
        error_message = f"Ошибка при загрузке питч-дека: {str(e)}"
        print(error_message)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_message)

# ✅ 3.1.Получить профиль фаундера
@router.get("/founders/profile", summary="Получить профиль фаундера", tags=["Startups"])
async def get_founder_profile(current_user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Startup).where(Startup.founder_id == current_user.user_id))
    startup = result.scalars().first()

    if not startup:
        raise HTTPException(status_code=404, detail="Стартап для фаундера не найден")

    return {
        "name": startup.name,
        "description": startup.description,
        "industry": startup.industry[0] if startup.industry else "",
        "stage": startup.stage[0] if startup.stage else "",
        "region": startup.region[0] if startup.region else "",
        "min_check": startup.min_check
    }

# ✅ 4. Создание стартапа (Заполнение шаблона с вопросами)
@router.post("/startups/fill_template", summary="Заполнить шаблон", tags=["Startups"])
async def fill_template(
    request: FillTemplateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    exists_stmt = select(exists().where(Startup.id == request.startup_id))
    startup_exists = await db.execute(exists_stmt)

    if not startup_exists.scalar():
        raise HTTPException(status_code=404, detail="Стартап не найден")

    scores = []
    for answer in request.answers:
        existing_score_stmt = select(StartupScore).where(
            StartupScore.startup_id == request.startup_id,
            StartupScore.category_id == answer.category_id,
            StartupScore.question_id == answer.question_id
        )
        existing_score = await db.execute(existing_score_stmt)
        existing_score = existing_score.scalars().first()

        if existing_score:
            existing_score.score = answer.score
        else:
            new_score = StartupScore(
                startup_id=request.startup_id,
                category_id=answer.category_id,
                question_id=answer.question_id,
                score=answer.score
            )
            db.add(new_score)
            scores.append(new_score)

    try:
        await db.flush()
        await db.commit()
        return jsonable_encoder({"message": "Шаблон успешно заполнен", "scores": [score.to_dict() for score in scores]})
    except Exception as e:
        logger.error(f"Ошибка сохранения данных: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail="Ошибка сохранения данных")

# ✅ 5. Получить скоринг стартапа
@router.get("/startups/{startup_id}/score", summary="Получить скоринг стартапа", tags=["Startups"])
async def get_startup_score(startup_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    exists_stmt = select(exists().where(Startup.id == startup_id))
    startup_exists = await db.execute(exists_stmt)

    if not startup_exists.scalar():
        raise HTTPException(status_code=404, detail="Стартап не найден")

    query = await db.execute(select(StartupScore).where(StartupScore.startup_id == startup_id))
    scores = query.scalars().all()

    if not scores:
        return jsonable_encoder({
            "message": "Оценки отсутствуют",
            "total_score": 0,
            "category_scores": {},
            "scores": []
        })

    return jsonable_encoder({
        "message": "Скоринг стартапа",
        "total_score": sum(score.score for score in scores),
        "category_scores": {score.category_id: 0 for score in scores},
        "scores": [score.to_dict() for score in scores]
    })

# ✅ 6. Фильтрация стартапов после матчинга
@router.post("/filter", summary="Фильтрация стартапов", tags=["Startups"])
async def filter_startups(
    filter_criteria: StartupFilterRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    if current_user.role != "investor":
        raise HTTPException(status_code=403, detail="Access denied")

    query = select(Startup)
    if filter_criteria.industry:
        query = query.where(Startup.industry.op("&&")(cast(filter_criteria.industry, ARRAY(VARCHAR))))
    if filter_criteria.stage:
        query = query.where(Startup.stage.op("&&")(cast(filter_criteria.stage, ARRAY(VARCHAR))))
    if filter_criteria.region:
        query = query.where(Startup.region.op("&&")(cast(filter_criteria.region, ARRAY(TEXT))))
    if filter_criteria.min_check:
        query = query.where(Startup.min_check <= filter_criteria.min_check)

    startup_result = await db.execute(query)
    filtered_startups = startup_result.scalars().all()

    return {
        "message": "Отфильтрованные стартапы",
        "startups": [
            {
                "id": s.id,
                "industry": s.industry,
                "stage": s.stage,
                "region": s.region,
                "min_check": s.min_check
            }
            for s in filtered_startups
        ]
    }

# ✅ 7. Получение информации о стартапе
@router.get("/{startup_id}", response_model=StartupResponse, summary="Получение информации о стартапе", tags=["Startups"])
async def get_startup_detail(startup_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Startup).filter(Startup.id == startup_id))
    startup = result.scalars().first()

    if not startup:
        raise HTTPException(status_code=404, detail="Стартап не найден")

    return StartupResponse.model_validate({
        "id": str(startup.id),
        "name": startup.name,
        "description": startup.description,
        "industry": ", ".join(startup.industry) if isinstance(startup.industry, list) else startup.industry,
        "stage": ", ".join(startup.stage) if isinstance(startup.stage, list) else startup.stage,
        "region": ", ".join(startup.region) if isinstance(startup.region, list) else startup.region,
        "min_check": startup.min_check,
        "pitch_deck": startup.pitch_deck,
        "created_at": startup.created_at.isoformat() if startup.created_at else None,
        "updated_at": startup.updated_at.isoformat() if startup.updated_at else None
    })
	
# ✅ 8. Отправка стартапа в Due Diligence
@router.post("/select/{startup_id}", summary="Отправить стартап в Due Diligence", tags=["Startups"])
async def submit_due_diligence(
    startup_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    result = await db.execute(select(Startup).filter(Startup.id == startup_id))
    startup = result.scalars().first()

    if not startup:
        raise HTTPException(status_code=404, detail="Стартап не найден")

    payload = {
        "startup_id": startup.id,
        "company_name": startup.company_name,
        "industry": startup.industry,
        "stage": startup.stage,
        "region": startup.region,
        "min_check": startup.min_check
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(DUE_DILIGENCE_SERVICE_URL, json=payload)
            response.raise_for_status()
            return {"message": "Стартап успешно отправлен в Due Diligence", "response": response.json()}
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=response.status_code, detail=f"Due Diligence error: {e.response.text}")

# ✅ 9. Получение списка подходящих стартапов для инвестора
@router.get("/matches/me", summary="Получить список стартапов, подходящих инвестору", tags=["Startups"])
async def get_matching_startups(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    if current_user.role != "investor":
        raise HTTPException(status_code=403, detail="Access denied")

    investor_result = await db.execute(select(User).where(User.id == current_user.user_id, User.role == "investor"))
    investor = investor_result.scalars().first()
    if not investor:
        raise HTTPException(status_code=404, detail="Инвестор не найден")

    if (
        not investor.investor_type
        or not investor.industry
        or not investor.investment_stage
        or not investor.region
        or investor.min_check is None or investor.min_check <= 0
    ):
        raise HTTPException(status_code=400, detail="Недостаточно данных для подбора стартапов")

    startup_result = await db.execute(
        select(Startup).where(
            Startup.industry.op("&&")(cast(investor.industry, ARRAY(VARCHAR))),
            Startup.stage.op("&&")(cast(investor.investment_stage, ARRAY(VARCHAR))),
            Startup.region.op("&&")(cast(investor.region, ARRAY(TEXT))),
            Startup.min_check <= investor.min_check
        )
    )

    matching_startups = startup_result.scalars().all()

    return {
        "message": "Найденные стартапы",
        "startups": [
            {
                "id": s.id,
                "name": s.name,
                "industry": s.industry,
                "stage": s.stage,
                "region": s.region,
                "min_check": s.min_check
            }
            for s in matching_startups
        ]
    }

# ✅ 10. Получение списка подходящих инвесторов для стартапа
@router.get("/investors/matches/me", summary="Получить список инвесторов, подходящих стартапу", tags=["Startups"])
async def get_matching_investors(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    if current_user.role != "founder":
        raise HTTPException(status_code=403, detail="Access denied")

    startup_result = await db.execute(select(Startup).where(Startup.founder_id == current_user.user_id))
    startup = startup_result.scalars().first()
    if not startup:
        raise HTTPException(status_code=404, detail="Стартап не найден")

    if not startup.industry or not startup.stage or not startup.region:
        raise HTTPException(status_code=400, detail="Недостаточно данных для подбора инвесторов")

    investor_result = await db.execute(
        select(User).where(
            User.role == "investor",
            User.industry.op("&&")(cast(startup.industry, ARRAY(TEXT))),
            User.investment_stage.op("&&")(cast(startup.stage, ARRAY(TEXT))),
            User.region.op("&&")(cast(startup.region, ARRAY(TEXT))),
            User.min_check >= startup.min_check
        )
    )

    matching_investors = investor_result.scalars().all()

    return {
        "message": "Найденные инвесторы",
        "investors": [
            {
                "id": i.id,
                "industry": i.industry,
                "investment_stage": i.investment_stage,
                "region": i.region,
                "min_check": i.min_check
            }
            for i in matching_investors
        ]
    }

# ✅ 11. Скоринг по pitch deck (analysis_results)

@router.get("/batch/pitch-scores", summary="Получить скоринги для нескольких стартапов", tags=["Startups"], response_model=StartupScoreBatchResponse)
async def get_batch_pitch_scores(
    ids: str = Query(..., description="Список startup_id через запятую"),
    db: AsyncSession = Depends(get_db),
    #current_user: CurrentUser = Depends(get_current_user)
):
    # Преобразуем строку в список UUID
    try:
        ids_list = [UUID(id_.strip()) for id_ in ids.split(",") if id_.strip()]
    except ValueError:
        raise HTTPException(status_code=400, detail="Один или несколько идентификаторов некорректны")

    if not ids_list:
        raise HTTPException(status_code=400, detail="Список идентификаторов пуст")

    # Дальше обычная логика
    subquery = (
        select(
            AnalysisResult.startup_id,
            func.max(AnalysisResult.created_at).label("max_created")
        )
        .where(AnalysisResult.startup_id.in_(ids_list))
        .group_by(AnalysisResult.startup_id)
        .subquery()
    )

    query = (
        select(
            AnalysisResult.startup_id,
            AnalysisResult.startup_score,
            AnalysisResult.usp_score,
            AnalysisResult.market_score,
            AnalysisResult.business_model_score,
            AnalysisResult.team_score,
            AnalysisResult.finance_score,
        )
        .join(subquery, (AnalysisResult.startup_id == subquery.c.startup_id) & (AnalysisResult.created_at == subquery.c.max_created))
    )

    results = await db.execute(query)

    scores = {
        str(row.startup_id): {
            "total": float(row.startup_score) if row.startup_score is not None else None,
            "usp": float(row.usp_score) if row.usp_score is not None else None,
            "market": float(row.market_score) if row.market_score is not None else None,
            "business_model": float(row.business_model_score) if row.business_model_score is not None else None,
            "team": float(row.team_score) if row.team_score is not None else None,
            "finance": float(row.finance_score) if row.finance_score is not None else None,
        }
        for row in results.all()
    }

    return scores

"""
@router.get("/batch/pitch-scores", summary="Получить скоринги для нескольких стартапов", tags=["Startups"], response_model=StartupScoreBatchResponse)
async def get_batch_pitch_scores(
    ids: Union[List[UUID], str] = Query(..., description="Список startup_id через запятую или несколько параметров"),
    db: AsyncSession = Depends(get_db),
    #current_user: CurrentUser = Depends(get_current_user)
):
    # Унификация формата ids
    if isinstance(ids, str):
        try:
            ids_list = [UUID(id_.strip()) for id_ in ids.split(",")]
        except ValueError:
            raise HTTPException(status_code=400, detail="Один или несколько идентификаторов некорректны")
    else:
        ids_list = ids  # Уже список UUID

    # Дальше работа как обычно
    subquery = (
        select(
            AnalysisResult.startup_id,
            func.max(AnalysisResult.created_at).label("max_created")
        )
        .where(AnalysisResult.startup_id.in_(ids_list))
        .group_by(AnalysisResult.startup_id)
        .subquery()
    )

    query = (
        select(
            AnalysisResult.startup_id,
            AnalysisResult.startup_score,
            AnalysisResult.usp_score,
            AnalysisResult.market_score,
            AnalysisResult.business_model_score,
            AnalysisResult.team_score,
            AnalysisResult.finance_score,
        )
        .join(subquery, (AnalysisResult.startup_id == subquery.c.startup_id) & (AnalysisResult.created_at == subquery.c.max_created))
    )

    results = await db.execute(query)

    scores = {
        str(row.startup_id): {
            "total": float(row.startup_score) if row.startup_score is not None else None,
            "usp": float(row.usp_score) if row.usp_score is not None else None,
            "market": float(row.market_score) if row.market_score is not None else None,
            "business_model": float(row.business_model_score) if row.business_model_score is not None else None,
            "team": float(row.team_score) if row.team_score is not None else None,
            "finance": float(row.finance_score) if row.finance_score is not None else None,
        }
        for row in results.all()
    }

    return scores
"""

"""
@router.get("/batch/pitch-scores", summary="Получить скоринги для нескольких стартапов", tags=["Startups"], response_model=StartupScoreBatchResponse)
async def get_batch_pitch_scores(
    ids: str = Query(..., description="Список startup_id через запятую"),
    db: AsyncSession = Depends(get_db),
    #current_user: CurrentUser = Depends(get_current_user)
):  
    # Разбираем строку в список UUID
    try:
        ids_list = [UUID(id_.strip()) for id_ in ids.split(",")]
    except ValueError:
        raise HTTPException(status_code=400, detail="Один или несколько идентификаторов некорректны")


    subquery = (
        select(
            AnalysisResult.startup_id,
            func.max(AnalysisResult.created_at).label("max_created")
        )
        .where(AnalysisResult.startup_id.in_(ids))
        .group_by(AnalysisResult.startup_id)
        .subquery()
    )

    query = (
        select(
            AnalysisResult.startup_id,
            AnalysisResult.startup_score,
            AnalysisResult.usp_score,
            AnalysisResult.market_score,
            AnalysisResult.business_model_score,
            AnalysisResult.team_score,
            AnalysisResult.finance_score,
        )
        .join(subquery, (AnalysisResult.startup_id == subquery.c.startup_id) & (AnalysisResult.created_at == subquery.c.max_created))
    )

    results = await db.execute(query)

    scores = {
        str(row.startup_id): {
            "total": float(row.startup_score) if row.startup_score is not None else None,
            "usp": float(row.usp_score) if row.usp_score is not None else None,
            "market": float(row.market_score) if row.market_score is not None else None,
            "business_model": float(row.business_model_score) if row.business_model_score is not None else None,
            "team": float(row.team_score) if row.team_score is not None else None,
            "finance": float(row.finance_score) if row.finance_score is not None else None,
        }
        for row in results.all()
    }

    return scores"""
