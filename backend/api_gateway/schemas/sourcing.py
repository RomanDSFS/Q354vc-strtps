import uuid
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class StartupFilterRequest(BaseModel):
    industry: Optional[List[str]] = None
    stage: Optional[List[str]] = None
    region: Optional[List[str]] = None
    min_check: Optional[float] = None

class StartupCreateRequest(BaseModel):
    industry: str
    stage: str
    region: str
    min_check: float

class InvestorProfileUpdate(BaseModel):
    investor_type: Optional[List[str]] = []
    investment_stage: Optional[List[str]] = []
    industry: Optional[List[str]] = []
    region: Optional[List[str]] = []
    min_check: Optional[float] = 0

class FounderProfileUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    stage: List[str] = Field(default_factory=list)
    industry: List[str] = Field(default_factory=list)
    region: List[str] = Field(default_factory=list)
    min_check: float = 20

class Answer(BaseModel):
    category_id: int
    question_id: int
    score: int = Field(..., ge=0, le=3)

class FillTemplateRequest(BaseModel):
    startup_id: uuid.UUID
    answers: List[Answer]

    @field_validator("startup_id", mode="before")
    @classmethod
    def convert_uuid(cls, value):
        if isinstance(value, uuid.UUID):
            return str(value)
        return value
