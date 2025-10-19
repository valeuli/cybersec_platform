from sqlalchemy import Column, String, Text, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.connection import Base
from sqlalchemy.orm import relationship

class Exam(Base):
    __tablename__ = "exam"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(Text)
    description = Column(Text)
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    results = relationship("UserExamResult", back_populates="exam", cascade="all, delete-orphan")