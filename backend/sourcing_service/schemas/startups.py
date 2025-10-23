from pydantic import BaseModel, Field, field_validator, RootModel
from typing import List, Optional, Dict
from uuid import UUID


# ✅ 0.0 Модель ответа стартапа
class StartupResponse(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    industry: str
    stage: str
    region: str
    min_check: float
    pitch_deck: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}


# ✅ 0.1 Профиль инвестора
class InvestorProfileUpdate(BaseModel):
    investor_type: Optional[List[str]] = []
    investment_stage: Optional[List[str]] = []
    industry: Optional[List[str]] = []
    region: Optional[List[str]] = []
    min_check: Optional[float] = 0


# ✅ 0.2 Профиль фаундера
class FounderProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    stage: List[str] = Field(default_factory=list)
    industry: List[str] = Field(default_factory=list)
    region: List[str] = Field(default_factory=list)
    min_check: float = 20


# ✅ 0.3 Фильтрация стартапов
class StartupFilterRequest(BaseModel):
    industry: Optional[List[str]] = None
    stage: Optional[List[str]] = None
    region: Optional[List[str]] = None
    min_check: Optional[float] = None


# ✅ 0.4 Ответ анкеты скоринга
class Answer(BaseModel):
    category_id: int
    question_id: int
    score: int = Field(..., ge=0, le=3, description="Score должен быть в диапазоне 0-3")


# ✅ 0.5 Запрос на заполнение шаблона оценки
class FillTemplateRequest(BaseModel):
    startup_id: UUID
    answers: List[Answer]

    @field_validator("startup_id", mode="before")
    @classmethod
    def convert_uuid(cls, value):
        if isinstance(value, UUID):
            return str(value)
        return value


# ✅ 0.6 Детальный скоринг
class StartupScoreDetails(BaseModel):
    total: float
    usp: float
    market: float
    business_model: float
    team: float
    finance: float


# ✅ 0.7 Батч-ответ скорингов (startup_id → details)
class StartupScoreBatchResponse(RootModel[Dict[UUID, StartupScoreDetails]]):
    pass
