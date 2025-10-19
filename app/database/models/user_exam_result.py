from sqlalchemy import Column, DateTime, func, ForeignKey, Numeric, String, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.connection import Base
from sqlalchemy.orm import relationship

class UserExamResult(Base):
    __tablename__ = "user_exam_result"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"))
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exam.id", ondelete="CASCADE"))
    total_score = Column(Numeric(5, 2))
    level_assigned = Column(String(20))
    taken_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint("level_assigned IN ('basic', 'intermediate', 'advanced')", name="check_level_assigned"),
    )

    user = relationship("User", back_populates="exam_results")
    exam = relationship("Exam", back_populates="results")
    answers = relationship("UserExamAnswer", back_populates="result", cascade="all, delete-orphan")