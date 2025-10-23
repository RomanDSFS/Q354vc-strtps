from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, text, Float, ARRAY, DateTime, func, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
#from database import Base
from sourcing_service.database import Base
from auth_service.models import RefreshToken


# ✅ Модель стартапов
class Startup(Base):
    __tablename__ = "startups"
    __table_args__ = {"extend_existing": True}  

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    founder_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    industry = Column(ARRAY(String), nullable=False)
    stage = Column(ARRAY(String), nullable=False)
    region = Column(ARRAY(String), nullable=False)
    min_check = Column(Float, nullable=False)
    pitch_deck = Column(String, nullable=True)  
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("now()"), onupdate=text("now()"))
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
# 🔹 Добавляем связь с оценками (не загружает автоматически, но можно использовать при `joinedload`)
    scores = relationship("StartupScore", back_populates="startup", cascade="all, delete-orphan")
    
# ✅ Модель `User`
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"extend_existing": True}

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)  # 🔹 Исправлено: теперь UUID
    email = Column(String, unique=True, nullable=False)
    company_name = Column(String, nullable=False)  #- И УБРАТЬ ИЗ tablename__ = "startups"МОДЕЛС СОУРС_СЕКВИС
    contacts = Column(String, nullable=False) #- И УБРАТЬ ИЗ МОДЕЛС СОУРС_СЕРВИС
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(String, nullable=False)  # 'investor' or 'founder'
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 🔹 Поля инвестора
    investor_type = Column(ARRAY(String), nullable=True)
    investment_stage = Column(ARRAY(String), nullable=True)
    industry = Column(ARRAY(String), nullable=True)  # ✅ Вернули industry
    region = Column(ARRAY(String), nullable=True)  # ✅ Вернули region
    min_check = Column(Float, nullable=True)

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    __table_args__ = {"extend_existing": True}
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    startup_id = Column(UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False)  # ✅ Правильная связь
    founder_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    file_path = Column(String, nullable=False)
    
    # ✅ Итоговый скоринг стартапа
    startup_score = Column(Float, nullable=False)

    # ✅ Расширенные метрики анализа
    usp_score = Column(Float, nullable=True)        # Уникальное торговое предложение (USP)
    market_score = Column(Float, nullable=True)     # Рынок
    business_model_score = Column(Float, nullable=True)  # Бизнес-модель
    team_score = Column(Float, nullable=True)       # Команда
    finance_score = Column(Float, nullable=True)    # Финансы

    created_at = Column(DateTime, server_default=func.now())

class StartupScore(Base):
    __tablename__ = "startup_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    startup_id = Column(UUID(as_uuid=True), ForeignKey("startups.id", ondelete="CASCADE"), nullable=False)  
    category_id = Column(Integer, nullable=False)  # 🔹 Добавлено хранение ID категории
    question_id = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)

    # 🔹 Связь с моделью стартапа (удобно для загрузки связанных данных)
    startup = relationship("Startup", back_populates="scores")

    # ✅ Метод для преобразования UUID в строку перед отправкой в JSON
    def to_dict(self):
        return {
            "id": str(self.id),  # ✅ UUID → str
            "startup_id": str(self.startup_id),  # ✅ UUID → str
            "category_id": self.category_id,
            "question_id": self.question_id,
            "score": self.score
        }
"""
class StartupScore(Base):
    __tablename__ = "startup_scores"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    startup_id = Column(ForeignKey("startups.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, nullable=False)
    score = Column(Integer, nullable=False)"""
  
