from sqlalchemy import Column, Text, Boolean, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.connection import Base
from sqlalchemy.orm import relationship

class Answer(Base):
    __tablename__ = "answer"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"))
    answer_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    question = relationship("Question", back_populates="answers")