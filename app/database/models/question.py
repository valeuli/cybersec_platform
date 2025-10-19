from sqlalchemy import Column, String, Text, Boolean, DateTime, func, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.connection import Base
from sqlalchemy.orm import relationship

class Question(Base):
    __tablename__ = "questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_text = Column(Text, nullable=False)
    level = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("level IN ('basic', 'intermediate', 'advanced')", name="check_question_level"),
    )

    answers = relationship("Answer", back_populates="question", cascade="all, delete-orphan")