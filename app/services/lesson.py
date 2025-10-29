from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.models.lesson import Lesson

def get_lesson_service(lesson_id: str, db: Session):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise HTTPException(status_code=404, detail="Módulo no encontrado")

    return {
        "id": str(lesson.id),
        "title": lesson.title,
        "content_type": lesson.content_type,
        "content_url": lesson.content_url,
        "text_content": lesson.text_content,
        "order_in_course": lesson.order_in_course,
    }