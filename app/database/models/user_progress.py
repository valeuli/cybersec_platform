from sqlalchemy import Column, DateTime, func, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.connection import Base
from sqlalchemy.orm import relationship

class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("user.id", ondelete="CASCADE"))
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lesson.id", ondelete="CASCADE"))
    last_accessed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="progresses")
    lesson = relationship("Lesson", back_populates="progresses")