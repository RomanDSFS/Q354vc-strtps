from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Query, Request
from fastapi.security import OAuth2PasswordBearer
from fastapi.encoders import jsonable_encoder
import httpx
import logging
import uuid
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from sourcing_service.routes.startups import FillTemplateRequest
from api_gateway.schemas.sourcing import (
    StartupFilterRequest, StartupCreateRequest, InvestorProfileUpdate,
    FounderProfileUpdate, Answer, FillTemplateRequest,)


router = APIRouter()

# 🔹 Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SOURCING_SERVICE_URL = "http://127.0.0.1:8002"
DUE_DILIGENCE_SERVICE_URL = "http://127.0.0.1:8005/kpi/analyze"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

"""
# ✅ 1. Получение всех стартапов
@router.get("/", summary="Получение всех стартапов", tags=["Startups"])
"""

# ✅ 1. Обновление профиля инвестора
@router.post("/investors/profile", summary="Обновление профиля инвестора", tags=["Startups"])
async def save_investor_profile(
    investor_data: InvestorProfileUpdate,  # ✅ Pydantic-модель вместо dict
    token: str = Depends(oauth2_scheme)
):
    headers = {"Authorization": f"Bearer {token}"}
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SOURCING_SERVICE_URL}/startups/investors/profile",
            json=investor_data.model_dump(),  # ✅ Исправленный метод для Pydantic v2
            headers=headers
        )
        
        if response.status_code != 200:
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except Exception:
                error_detail = "Invalid response from sourcing service"

            raise HTTPException(status_code=response.status_code, detail=error_detail)
        
        return response.json()


# ✅ 2. Обновление профиля основателя
@router.post("/founders/profile", summary="Обновление профиля основателя", tags=["Startups"])
async def save_founder_profile(
    founder_data: FounderProfileUpdate,
    token: str = Depends(oauth2_scheme)
):
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SOURCING_SERVICE_URL}/startups/founders/profile",
            json=founder_data.model_dump(),  # ✅ Передаем корректный JSON
            headers=headers
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))

        return response.json()

# ✅ 3. Загрузка Pitch Deck и анализ
@router.post("/founders/upload", summary="Загрузить Pitch Deck и провести анализ", tags=["Startups"])
async def upload_pitch_deck(file: UploadFile = File(...), token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}
    
    TIMEOUT = 240.0  # Увеличиваем таймаут до 4 минут

    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        files = {"file": (file.filename, await file.read(), file.content_type)}
        response = await client.post(f"{SOURCING_SERVICE_URL}/startups/founders/upload", files=files, headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        
        return response.json()
    
# ✅ 3.1. Получить профиль фаундера 
@router.get("/founders/profile", summary="Получить профиль фаундера", tags=["Startups"])
async def proxy_get_founder_profile(token: str = Depends(oauth2_scheme)):
    try:
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SOURCING_SERVICE_URL}/startups/founders/profile",
                headers=headers
            )

        if response.status_code != 200:
            try:
                error_detail = response.json().get("detail", "Ошибка внешнего сервиса")
            except Exception:
                error_detail = response.text or "Ошибка внешнего сервиса"

            raise HTTPException(
                status_code=response.status_code,
                detail=error_detail
            )

        return response.json()

    except Exception as e:
        logger.exception("Ошибка получения профиля фаундера")
        raise HTTPException(status_code=500, detail="Ошибка при получении профиля фаундера")


# ✅ 4. Создание стартапа "Заполнить шаблон"
@router.post("/startups/fill_template", summary="Заполнить шаблон", tags=["Startups"])
async def fill_template(data: FillTemplateRequest, token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}

    try:
        # 🔹 Конвертируем `UUID` в строку перед отправкой
        request_data = jsonable_encoder(data)

        async with httpx.AsyncClient() as client:
            response = await client.post(f"{SOURCING_SERVICE_URL}/startups/startups/fill_template", json=request_data, headers=headers)

        if response.status_code != 200:
            logger.error(f"Ошибка проксирования: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))

        return response.json()

    except httpx.RequestError as e:
        logger.error(f"Ошибка соединения с sourcing_service: {e}")
        raise HTTPException(status_code=502, detail="Ошибка соединения с сервисом заполнения шаблонов")

    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


# ✅ 5.**Получение скоринга стартапа**
@router.get("/startups/{startup_id}/score", summary="Получить скоринг стартапа после анализа шаблона", tags=["Startups"])
async def get_startup_score(startup_id: uuid.UUID, token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SOURCING_SERVICE_URL}/startups/startups/{startup_id}/score", headers=headers)

        if response.status_code != 200:
            logger.error(f"Ошибка проксирования: {response.status_code} - {response.text}")
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))

        return response.json()

    except httpx.RequestError as e:
        logger.error(f"Ошибка соединения с sourcing_service: {e}")
        raise HTTPException(status_code=502, detail="Ошибка соединения с сервисом скоринга стартапов")

    except Exception as e:
        logger.error(f"Непредвиденная ошибка: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")

    
# ✅ 5. Фильтрация стартапов через API Gateway
@router.post("/filter", summary="Фильтрация стартапов", tags=["Startups"])
async def filter_startups(
    filters: StartupFilterRequest,
    token: str = Depends(oauth2_scheme)  # 🔹 Проверяем токен
):
    headers = {"Authorization": f"Bearer {token}"}  # ✅ Передаем токен

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{SOURCING_SERVICE_URL}/startups/filter",
                json=filters.model_dump(),  # ✅ Современный метод вместо `.dict()`
                headers=headers  # ✅ Передаем токен в заголовках
            )
            response.raise_for_status()  # ✅ Проверяем ошибки HTTP

            return response.json()  # ✅ Возвращаем успешный JSON-ответ
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка: {e.response.text}")
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Ошибка соединения с sourcing_service")
        except ValueError:  # ✅ JSONDecodeError
            raise HTTPException(status_code=500, detail="Ошибка обработки JSON-ответа")

# ✅ 7. Получение информации о стартапе
@router.get("/{startup_id}", summary="Получение информации о стартапе", tags=["Startups"])
async def get_startup_detail(startup_id: str):
    TIMEOUT = 30.0  # Увеличиваем таймаут до 2 минут
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        response = await client.get(f"{SOURCING_SERVICE_URL}/startups/{startup_id}")
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        
        return response.json()

# ✅ 8. Отправка стартапа в Due Diligence
@router.post("/select/{startup_id}", summary="Отправить стартап в Due Diligence", tags=["Startups"])
async def submit_due_diligence(startup_id: str, token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{SOURCING_SERVICE_URL}/select/{startup_id}", headers=headers)
        
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.json().get("detail"))
        
        return response.json()
    
# ✅ 9. Получение списка подходящих стартапов для инвестора
@router.get("/matches/me", summary="Получить список стартапов, подходящих инвестору", tags=["Startups"])
async def get_matching_startups(token: str = Depends(oauth2_scheme)):
    headers = {"Authorization": f"Bearer {token}"}

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SOURCING_SERVICE_URL}/startups/matches/me", headers=headers)
            response.raise_for_status()

            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка: {e.response.text}")
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Ошибка соединения с sourcing_service")
        except ValueError:
            raise HTTPException(status_code=500, detail="Ошибка обработки JSON-ответа")

"""
@router.get("/matches/{investor_id}", summary="Получить список стартапов, подходящих инвестору", tags=["Startups"])
async def get_matching_startups(investor_id: str, token: str = Depends(oauth2_scheme)):  
    headers = {"Authorization": f"Bearer {token}"}  # ✅ Передаем токен

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SOURCING_SERVICE_URL}/startups/matches/{investor_id}", headers=headers)
            response.raise_for_status()  # ✅ Проверяем ошибки HTTP

            return response.json()  # ✅ Возвращаем успешный JSON-ответ
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка: {e.response.text}")
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Ошибка соединения с sourcing_service")
        except ValueError:  # ✅ JSONDecodeError
            raise HTTPException(status_code=500, detail="Ошибка обработки JSON-ответа")"""

# ✅ 10. Получение списка подходящих инвесторов для стартапа
@router.get("/investors/matches/{founder_id}", summary="Получить список инвесторов, подходящих стартапу", tags=["Startups"])
async def get_matching_investors(founder_id: str, token: str = Depends(oauth2_scheme)):  
    headers = {"Authorization": f"Bearer {token}"}  # ✅ Передаем токен

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{SOURCING_SERVICE_URL}/startups/investors/matches/{founder_id}", headers=headers)
            response.raise_for_status()  # ✅ Проверяем ошибки HTTP

            return response.json()  # ✅ Возвращаем успешный JSON-ответ
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"Ошибка: {e.response.text}")
        except httpx.RequestError:
            raise HTTPException(status_code=502, detail="Ошибка соединения с sourcing_service")
        except ValueError:  # ✅ JSONDecodeError
            raise HTTPException(status_code=500, detail="Ошибка обработки JSON-ответа")


# ✅ 11. Скоринг по pitch deck (analysis_results)
@router.get("/batch/pitch-scores", summary="Скоринг по pitch deck (analysis_results)", tags=["Startups"])
async def proxy_batch_pitch_scores(request: Request, ids: str = Query(...)):
    """
    Прокси эндпоинт для получения скоринга стартапов из сервиса sourcing_service.
    Передает Authorization-заголовок и параметры запроса.
    """
    try:
        ids_list = ids.split(",")
        url = f"{SOURCING_SERVICE_URL}/startups/batch/pitch-scores"

        headers = {}
        # Прокси заголовка авторизации
        if "authorization" in request.headers:
            headers["Authorization"] = request.headers["authorization"]

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                url,
                params={"ids": ",".join(ids_list)},
                headers=headers,
            )

        if response.status_code == 200:
            return response.json()

        # Если sourcing_service вернул ошибку — пробрасываем её клиенту
        try:
            error_detail = response.json().get("detail", "Ошибка внешнего сервиса")
        except Exception:
            error_detail = response.text or "Ошибка внешнего сервиса"

        logger.error(f"Ошибка при запросе к sourcing_service: {response.status_code} - {error_detail}")
        raise HTTPException(
            status_code=response.status_code,
            detail=error_detail
        )

    except HTTPException as e:
        # Если уже кинули HTTPException, пробрасываем дальше без изменений
        raise e

    except httpx.RequestError as e:
        logger.exception("Ошибка соединения с sourcing_service")
        raise HTTPException(status_code=502, detail="Ошибка соединения с внешним сервисом")
    
    except Exception:
        logger.exception("Неожиданная ошибка при получении batch pitch-scores")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера при получении скорингов")
