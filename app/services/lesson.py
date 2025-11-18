from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.database.models.lesson import Lesson
from app.database.models.user import User
from app.database.models.user_progress import UserProgress
from app.services.quiz import get_user_level

LEVEL_RANGES = {
  "basic": (1,5),
  "intermediate": (6,10),
  "advanced": (11,15)
}

def get_lesson_service(lesson_id: str, db: Session):
    try:
        lesson_uuid = UUID(lesson_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="ID inválido")

    lesson = db.query(Lesson).filter(Lesson.id == lesson_uuid).first()
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

def get_lessons_by_level(db: Session, current_user: User):
    level_data = get_user_level(db, current_user)
    user_level = level_data["level"]

    start, end = LEVEL_RANGES.get(user_level, (1, 5))
    lessons = (
        db.query(Lesson)
        .filter(Lesson.order_in_course >= start, Lesson.order_in_course <= end)
        .order_by(Lesson.order_in_course)
        .all()
    )

    if not lessons:
        raise HTTPException(status_code=404, detail="No módulos para este nivel.")

    progress = (
        db.query(UserProgress)
        .filter(UserProgress.user_id == current_user.id)
        .all()
    )

    seen_ids = {str(p.lesson_id) for p in progress}
    next_lesson = next((l for l in lessons if str(l.id) not in seen_ids), None)

    if next_lesson:
        start_index = lessons.index(next_lesson)
    else:
        start_index = 0

    lessons_to_show = lessons[start_index:start_index + 3]

    return {
        "level": user_level,
        "next_lesson_id": str(next_lesson.id) if next_lesson else None,
        "lessons": [
            {
                "id": str(l.id),
                "title": l.title,
                "content_type": l.content_type,
                "content_url": l.content_url,
                "text_content": l.text_content,
                "order_in_course": l.order_in_course
            }
            for l in lessons_to_show
        ]
    }


def get_next_lesson_navigation(lesson_id: str, db: Session):
    current = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not current:
        raise HTTPException(status_code=404, detail="Lección no encontrada")

    previous_lesson = (
        db.query(Lesson)
        .filter(Lesson.order_in_course < current.order_in_course)
        .order_by(Lesson.order_in_course.desc())
        .first()
    )
    next_lesson = (
        db.query(Lesson)
        .filter(Lesson.order_in_course > current.order_in_course)
        .order_by(Lesson.order_in_course.asc())
        .first()
    )

    return {
        "current_lesson_id": str(current.id),
        "previous_lesson_id": str(previous_lesson.id) if previous_lesson else None,
        "next_lesson_id": str(next_lesson.id) if next_lesson else None
    }
