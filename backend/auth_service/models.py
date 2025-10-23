from sqlalchemy import Column, String, TIMESTAMP, ForeignKey, text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from auth_service.database import Base

# ✅ Модель пользователя
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))
    email = Column(String, unique=True, index=True, nullable=False)
    company_name = Column(String, nullable=False)  #- И УБРАТЬ ИЗ МОДЕЛС СОУРС_СЕКВИС
    contacts = Column(String, nullable=False) #- И УБРАТЬ ИЗ МОДЕЛС СОУРС_СЕКВИС
    password_hash = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    role = Column(String, nullable=False)  # investor, founder, admin
    created_at = Column(TIMESTAMP, server_default=text("now()"))
    updated_at = Column(TIMESTAMP, server_default=text("now()"), onupdate=text("now()"))

# ✅ Таблица для хранения Refresh-токенов
class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
