from pydantic import BaseModel, UUID4, ConfigDict
from typing import List, Optional, Literal

class LessonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    title: str
    content_type: Literal["video", "texto"]
    content_url: Optional[str]
    text_content: Optional[str]
    order_in_course: int


class UserLessonsOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    level: Literal["inicial", "básico", "intermedio", "avanzado"]
    next_lesson_id: Optional[UUID4]
    lessons: List[LessonOut]