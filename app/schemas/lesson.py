from pydantic import BaseModel, UUID4
from typing import Optional, Literal

class LessonOut(BaseModel):
    id: UUID4
    title: str
    content_type: Literal["video", "texto"]
    content_url: Optional[str]
    text_content: Optional[str]
    order_in_course: int

    class Config:
        from_attributes = True