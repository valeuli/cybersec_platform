from sqlalchemy import Column, DateTime, func, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.connection import Base
from sqlalchemy.orm import relationship

class UserExamAnswer(Base):
    __tablename__ = "user_exam_answer"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    result_id = Column(UUID(as_uuid=True), ForeignKey("user_exam_result.id", ondelete="CASCADE"))
    question_id = Column(UUID(as_uuid=True), ForeignKey("questions.id", ondelete="CASCADE"))
    answer_id = Column(UUID(as_uuid=True), ForeignKey("answer.id", ondelete="CASCADE"))
    is_correct = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    result = relationship("UserExamResult", back_populates="answers")
    question = relationship("Question")
    answer = relationship("Answer")