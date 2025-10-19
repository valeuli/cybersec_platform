from sqlalchemy import Column, String, Integer, Text, DateTime, func, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database.connection import Base
from sqlalchemy.orm import relationship

class Course(Base):
    __tablename__ = "course"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    level = Column(String(20), nullable=False)
    order_in_level = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("level IN ('básico', 'intermedio', 'avanzado')", name="check_course_level"),
    )

    lessons = relationship("Lesson", back_populates="course", cascade="all, delete-orphan")