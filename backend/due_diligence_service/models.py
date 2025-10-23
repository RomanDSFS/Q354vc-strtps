from sqlalchemy import Column, String, Numeric, ForeignKey, TIMESTAMP, text
from sqlalchemy.dialects.postgresql import UUID
import uuid
from database import Base

# ✅ Модель хранения стартапов в Due Diligence
class DueDiligenceStartup(Base):
    __tablename__ = "due_diligence_startups"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    startup_id = Column(UUID(as_uuid=True), unique=True, nullable=False)
    company_name = Column(String, nullable=False)
    industry = Column(String, nullable=False)
    stage = Column(String, nullable=False)
    region = Column(String, nullable=False)
    min_check = Column(Numeric, nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("now()"))
