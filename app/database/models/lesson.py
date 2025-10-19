from sqlalchemy import Column, String, Integer, Text, DateTime, func, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.connection import Base
from sqlalchemy.orm import relationship

class Lesson(Base):
    __tablename__ = "lesson"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("course.id", ondelete="CASCADE"))
    content_type = Column(String(10), nullable=False)
    title = Column(Text)
    content_url = Column(String(200))
    text_content = Column(Text)
    order_in_course = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("content_type IN ('video', 'texto')", name="check_content_type"),
    )

    course = relationship("Course", back_populates="lessons")
    progresses = relationship("UserProgress", back_populates="lesson", cascade="all, delete-orphan")